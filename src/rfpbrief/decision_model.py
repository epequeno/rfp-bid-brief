"""The decision census: every decision model served, one frozen request, one pre-registered τ.

## The rule, and why it is a census

Naming a panel of three models means defending the choice of three. *Every non-alias decision model
served on a recorded date* has no selection bias to defend, and at roughly $0.00002 per decision the
cost of the whole census is a fraction of a cent — so the judgement call buys nothing and costs
credibility.

Three disciplines make the comparison mean something (ADR 0009):

1. **Byte-identical inputs.** Every model receives the same `state` and the same `questions`; only
   the `model` field differs. The Decisions API is a passthrough of one schema, so this is literally
   true rather than approximately true — which is the entire reason the comparison is meaningful.
2. **One threshold for every model.** τ = 0.50 is read from the frozen labels file and applied
   unchanged. A model whose probabilities need a different threshold is a model that is not calibrated
   at τ, and that is a **finding**, not a configuration to fix. Per-model optimal thresholds are
   computed and reported separately, labelled post-hoc, never as the headline.
3. **Pinned canonical slugs.** Aliases (`~typesafe/jev-latest`) move to a new build without notice, so
   they are excluded by rule. Every result records the resolved model version and the serving
   provider returned by the API, because the same weights behind a different host is a different
   reproducibility story.

## What it does not buy

Statistical power. Fourteen models over eleven fixtures is 154 decisions and still **eleven
independent label comparisons per model**. Several thin calibration curves are still thin, and the
sample size is printed next to every one of them.

Calls are injectable, so the whole pipeline is testable offline and no test spends money.
"""

from __future__ import annotations

import json
import itertools
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from . import providers
from .extract import Extraction
from .spans import Document

REPO = Path(__file__).resolve().parents[2]
DECISIONS_URL = "https://openrouter.ai/api/alpha/decisions"

# ADR 0008 pins these two. The census resolves each to a *dated build* at call time, and the resolved
# version is what gets reported: the same weights behind another host is a different measurement.
CHANNEL = "typesafe/jev-1.13"
COMPARATOR = "microsoft/microsoft-decision-1"

# Frozen. Changing either of these invalidates every number produced before the change, so they are
# constants with a hash rather than prompt strings assembled at the call site.
QUESTION = "Should this firm bid on this solicitation?"
INSTRUCTIONS = (
    "Answer yes if this firm should bid on this solicitation under the bidder profile in the state, "
    "and no if any delivery model or capability the profile excludes applies to it. Weigh only the "
    "state; do not assume anything not stated there."
)
STATE_HEADER = "BIDDER PROFILE"
FACTS_HEADER = "SOLICITATION FACTS"
REQUIREMENTS_HEADER = "REQUIREMENTS AS FOUND"


def frozen_request_sha256() -> str:
    """Hash of the frozen request text, so a result can be tied to the exact question asked."""
    import hashlib
    blob = "\n".join([QUESTION, INSTRUCTIONS, STATE_HEADER, FACTS_HEADER, REQUIREMENTS_HEADER]).encode()
    return hashlib.sha256(blob).hexdigest()


def build_state(profile: dict, extraction: Extraction) -> str:
    """The state every model sees. Deterministic: same inputs, same bytes, no dict-order surprises."""
    lines: list[str] = [STATE_HEADER]
    lines.append(profile.get("summary", "").strip())
    lines.append("")
    lines.append("Excluded delivery models:")
    for item in profile.get("excluded_delivery_models", []):
        lines.append(f"- {item}")
    lines.append("Excluded capability areas:")
    for item in profile.get("excluded_capability_areas", []):
        lines.append(f"- {item}")
    # The rules of thumb are part of what the profile excludes — see the consistency test, which
    # fails if any phrase the deterministic layer cites is missing here. Omitting them once made
    # every model read the profile literally, and the phrase naming the D365 case was invisible to
    # all fourteen while the rules layer could still cite it.
    rules = profile.get("decision_rules_of_thumb", [])
    if rules:
        lines.append("Rules of thumb:")
        for item in rules:
            lines.append(f"- {item}")
    lines.append("Base: " + str((profile.get("bidder") or {}).get("base", "")))

    lines += ["", FACTS_HEADER]
    for name, fact in extraction.facts.items():
        lines.append(f"- {name}: {fact.value}")

    lines += ["", REQUIREMENTS_HEADER]
    for name, fact in extraction.requirements.items():
        value = json.dumps(fact.value) if not isinstance(fact.value, str) else fact.value
        lines.append(f"- {name}: {value}")
        for c in fact.citations:
            lines.append(f'    evidence ({c.page}): "{c.quote}"')
    return "\n".join(lines).strip() + "\n"


def request_body(model: str, state: str) -> dict:
    """The frozen request. Identical for every model except the model field."""
    return {
        "model": model,
        "state": state,
        "questions": {"bid": {"type": "noul", "instructions": QUESTION + " " + INSTRUCTIONS}},
    }


# ── the census: which models exist, by rule rather than by memory ─────────────────────────────

@dataclass
class Candidate:
    id: str
    canonical: str
    context_length: int
    price_in_per_m: float
    created: int | None
    excluded_because: str = ""

    @property
    def eligible(self) -> bool:
        return not self.excluded_because


def census(fetch: Callable[[str], tuple[int, str]] = providers._get) -> tuple[list[Candidate], str]:
    """Every decision model served now, filtered by rule, with the date it was taken.

    The list is not curated. Anything filtered out is filtered by a rule stated here, so a reader can
    disagree with the rule rather than wonder at the selection.
    """
    status, body = fetch(
        "https://openrouter.ai/api/v1/models?output_modalities=decisions"
    )
    if status != 200:
        raise RuntimeError(f"census unavailable: HTTP {status} {body[:200]}")
    taken = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    by_canonical: dict[str, Candidate] = {}
    for m in json.loads(body).get("data", []):
        mid = m["id"]
        canonical = (m.get("canonical_slug") or mid).lstrip("~")
        price = m.get("pricing") or {}
        try:
            price_in = float(price.get("prompt") or 0) * 1e6
        except (TypeError, ValueError):
            price_in = 0.0
        candidate = Candidate(id=mid, canonical=canonical,
                              context_length=int(m.get("context_length") or 0),
                              price_in_per_m=price_in, created=m.get("created"))
        # Rules, in order. Each exclusion is recorded on the candidate so the report can show it.
        if mid.startswith("~"):
            candidate.excluded_because = "alias — moves to a new build without notice"
        elif mid.endswith(":free"):
            candidate.excluded_because = "free tier of an entry already counted"
        elif candidate.context_length <= 0:
            candidate.excluded_because = "no declared context length for state plus questions"

        existing = by_canonical.get(canonical)
        if existing is None or (existing.excluded_because and candidate.eligible):
            by_canonical[canonical] = candidate

    return sorted(by_canonical.values(), key=lambda c: (not c.eligible, c.canonical)), taken


# ── asking, and recording what answered ───────────────────────────────────────────────────────

def _post(url: str, payload: dict, timeout: int = 120) -> tuple[int, str]:
    return providers._post(url, payload, timeout)


@dataclass
class Answer:
    model: str
    status: int
    noul: float | None = None
    resolved: str | None = None
    provider: str | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    cost: float | None = None
    error: str = ""

    @property
    def ok(self) -> bool:
        return self.status == 200 and self.noul is not None


def ask(model: str, state: str, post: Callable[[str, dict], tuple[int, str]] = _post) -> Answer:
    """One decision. Records the version and host that actually served it."""
    status, body = post(DECISIONS_URL, request_body(model, state))
    if status != 200:
        try:
            message = json.loads(body).get("error", {}).get("message", body[:160])
        except Exception:
            message = body[:160]
        return Answer(model=model, status=status, error=" ".join(str(message).split())[:220])
    try:
        payload = json.loads(body)
        answer = payload["answers"]["bid"]
        usage = payload.get("usage") or {}
        return Answer(
            model=model, status=status, noul=float(answer["noul"]),
            resolved=payload.get("model"), provider=payload.get("provider"),
            input_tokens=usage.get("input_tokens"), output_tokens=usage.get("output_tokens"),
            cost=usage.get("cost"),
        )
    except Exception as exc:
        return Answer(model=model, status=status, error=f"unreadable answer: {exc}")


@dataclass
class Census:
    taken: str
    request_sha256: str
    tau: float
    candidates: list[Candidate] = field(default_factory=list)
    answers: list[dict] = field(default_factory=list)
    state_sha256: str = ""

    def state_digest(self) -> str:
        """The state every model was shown, independent of the answers it gave."""
        import hashlib
        return hashlib.sha256(
            "".join(f'{a.get("fixture")}\x00{a.get("state_sha256")}\x00' for a in self.answers).encode()
        ).hexdigest()

    def answers_digest(self) -> str:
        """The measurement itself. Two runs of an unchanged state differ here, and that difference is
        the thing a repeat is for — so it belongs in the filename, not only in the file."""
        import hashlib
        return hashlib.sha256(
            "".join(f'{a.get("fixture")}\x00{a.get("model_requested")}\x00{a.get("noul")}\x00'
                    for a in self.answers).encode()
        ).hexdigest()

    def digest(self) -> str:
        """Content-addressed identity, enough to tell any two censuses apart for good."""
        return f"{self.state_digest()[:8]}-{self.answers_digest()[:8]}"

    def to_json(self) -> dict:
        return {
            "schema": "decisions/1",
            "taken": self.taken,
            "request_sha256": self.request_sha256,
            "question": QUESTION,
            "instructions": INSTRUCTIONS,
            "operating_point_tau": self.tau,
            "state_sha256": self.state_sha256 or self.digest(),
            "note": (
                "Every model receives the same state and the same questions; only the model field "
                "differs. tau is the pre-registered operating point from fixtures/labels.json and is "
                "applied unchanged to every model (ADR 0009)."
            ),
            "models": [
                {"id": c.id, "canonical": c.canonical, "context_length": c.context_length,
                 "price_in_per_m": c.price_in_per_m, "eligible": c.eligible,
                 "excluded_because": c.excluded_because}
                for c in self.candidates
            ],
            "answers": self.answers,
        }


def run(
    fixtures: list[tuple[Document, Extraction]],
    profile: dict,
    candidates: list[Candidate],
    tau: float,
    taken: str,
    ask_fn: Callable[[str, str], Answer] = ask,
) -> Census:
    """Ask every eligible model about every fixture. One frozen state per fixture, reused byte for byte."""
    census_out = Census(taken=taken, request_sha256=frozen_request_sha256(), tau=tau,
                        candidates=candidates)
    eligible = [c for c in candidates if c.eligible]
    states = {doc.fixture: build_state(profile, ex) for doc, ex in fixtures}
    for candidate in eligible:
        for doc, _ex in fixtures:
            answer = ask_fn(candidate.canonical, states[doc.fixture])
            census_out.answers.append({
                "fixture": doc.fixture,
                "state_sha256": __import__("hashlib").sha256(states[doc.fixture].encode()).hexdigest(),
                "model_requested": candidate.id,
                "model_canonical": candidate.canonical,
                "status": answer.status,
                "noul": answer.noul,
                "resolved_model": answer.resolved,
                "provider": answer.provider,
                "input_tokens": answer.input_tokens,
                "output_tokens": answer.output_tokens,
                "cost": answer.cost,
                "error": answer.error,
            })
    return census_out
