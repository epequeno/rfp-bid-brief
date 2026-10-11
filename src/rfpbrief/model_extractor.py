"""The model-backed extractor, with the citation gate wired back into it as a repair channel.

ADR 0006 is the reason this module exists rather than a shell one-liner. The gate does not merely
accept or reject: when it rejects, it reports *where the quote actually is* ("this quote does appear
in p2-s0, p2-s1, p4-s0"). Throwing that away and failing the fixture wastes the most useful signal
the pipeline produces. So a refusal is fed back for **one** bounded attempt to correct it, and the
attempt count travels with the extraction.

Two disciplines keep the retry honest:

* **Bounded.** One retry, not a loop. A producer that cannot fix a citation in one attempt with the
  location spelled out has a problem this pipeline cannot repair, and an unbounded loop would turn a
  measurement into a search.
* **Not a second chance at the answer.** The repair prompt names the refused citations and says to
  change only what is necessary. It is a repair channel, not a re-roll: if the retry changed the
  requirement values too, the metric would be measuring reruns.

The caller is injectable, so the whole loop is tested offline with a stub that returns a broken
citation and then a fixed one.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from . import extract as extract_mod
from . import spans
from .spans import Document

REPO = Path(__file__).resolve().parents[2]
PROMPT_PATH = REPO / "extract" / "prompt.md"
DEFAULT_MODEL = "openrouter/minimax/minimax-m2.7"

REPAIR_TEMPLATE = """
---

Your previous answer was **refused by the citation gate**. Return the same JSON object again, with
the refusals fixed and **everything else unchanged** — do not revise values, do not add fields, do
not drop fields. The frozen values are the measurement; the citations are what is broken.

Refusals:

{problems}

Standard for a fix: the quote must be copied character for character out of the span you cite, and
it must sit either inside that span or on that span's page. If the words you want run across two
spans, quote only the part that is inside one of them.

Your previous answer:

```json
{previous}
```
"""


def prompt_text() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


def prompt_sha256() -> str:
    return hashlib.sha256(PROMPT_PATH.read_bytes()).hexdigest()


def payload_for(doc: Document) -> str:
    lines = [f"fixture: {doc.fixture}", f"pages: {len(doc.pages)}  spans: {len(doc.spans)}", ""]
    for s in doc.spans:
        lines.append(f"[{s.id}] (page {s.page}) {spans.collapse_ws(s.text)}")
    return "\n".join(lines)


def call_pi(prompt: str, model: str) -> str:
    """One model call. No tools, no session: the model sees the prompt and nothing else."""
    res = subprocess.run(
        ["pi", "-p", "--no-session", "--no-tools", "--model", model, "--mode", "text", prompt],
        capture_output=True, text=True, timeout=1800,
    )
    if res.returncode != 0:
        raise RuntimeError(f"pi exited {res.returncode}: {res.stderr[-400:]}")
    return res.stdout


def _strip_fences(text: str) -> str:
    body = text.strip()
    if body.startswith("```"):
        body = body.split("\n", 1)[1] if "\n" in body else body
        body = body.rsplit("```", 1)[0]
    return body.strip()


@dataclass
class ModelRun:
    fixture: str
    model: str
    attempts: int = 0
    data: dict | None = None
    refusals: list[dict] = field(default_factory=list)
    error: str | None = None

    @property
    def repaired(self) -> bool:
        return self.attempts > 1 and self.data is not None

    @property
    def accepted(self) -> bool:
        return self.data is not None

    @property
    def first_attempt_problems(self) -> list[str]:
        return self.refusals[0]["problems"] if self.refusals else []


def extract(
    doc: Document,
    model: str = DEFAULT_MODEL,
    retries: int = 1,
    caller: Callable[[str, str], str] = call_pi,
) -> ModelRun:
    """Run the extractor, feeding a citation refusal back once. Never invents a citation itself."""
    run = ModelRun(fixture=doc.fixture, model=model)
    prompt = prompt_text()
    payload = payload_for(doc)
    previous: str | None = None

    for attempt in range(1, retries + 2):
        run.attempts = attempt
        full = f"{prompt}\n\nHere is the document.\n\n{payload}"
        if previous is not None:
            full = f"{prompt}{REPAIR_TEMPLATE.format(problems=chr(10).join('- ' + p for p in run.refusals[-1]['problems']), previous=previous)}\n\nHere is the document.\n\n{payload}"
        try:
            raw = caller(full, model)
        except Exception as exc:  # network, quota, timeout
            run.error = f"model call failed on attempt {attempt}: {exc}"
            return run

        try:
            data = json.loads(_strip_fences(raw))
        except json.JSONDecodeError as exc:
            run.refusals.append({"attempt": attempt, "problems": [f"response was not JSON: {exc}"]})
            previous = _strip_fences(raw)
            continue

        problems = extract_mod.validate(doc, data)
        if not problems:
            run.data = data
            return run
        run.refusals.append({"attempt": attempt, "problems": problems})
        previous = json.dumps(data, ensure_ascii=False)

    return run


def annotate(run: ModelRun, data: dict, started: str, finished: str) -> dict:
    """Attach what produced it. A number without the model id and prompt hash is not a result."""
    data = dict(data)
    data["schema"] = "extraction/1"
    data["produced_by"] = f"pi -p --no-session --no-tools --model {run.model}"
    data["extractor"] = {
        "model": run.model,
        "prompt": "extract/prompt.md",
        "prompt_sha256": prompt_sha256(),
        "attempts": run.attempts,
        "repaired_after_refusal": run.repaired,
        "refusals": run.refusals,
        "started_utc": started,
        "finished_utc": finished,
        "inputs": "spans only (rfpbrief payload): no label, no bidder profile, no hand-authored extraction",
    }
    return data
