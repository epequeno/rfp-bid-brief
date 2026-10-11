"""Is the decision model we want callable *today*? A probe, not a recollection.

The lesson this module was taught on 2026-10-11, the day it was written: **its first version tested the
wrong thing.** It treated a 404 from `/api/v1/models/<id>` as "not callable", reported that for
`typesafe/jev-router`, and was wrong — inference worked, and returned a decision with a probability.
A catalogue endpoint is metadata about a model; it is not the model.

So callability now means **we made a call and it answered**, and the catalogue and per-model signals
are reported as information rather than as the verdict. That costs one minimal completion per probe,
which is the price of not being confidently wrong about availability.

Both directions of staleness are real: a listing can precede an API, and an API can serve a model a
catalogue or an endpoint does not acknowledge.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

CATALOGUE = "https://openrouter.ai/api/v1/models"
MODEL_URL = "https://openrouter.ai/api/v1/models/{model}"
COMPLETIONS = "https://openrouter.ai/api/v1/chat/completions"
# Decision models are not chat models and they say so: the chat endpoint answers 400 with
# "… is a decisions model and cannot be used with the chat/completions endpoint. Use the
# /api/alpha/decisions endpoint instead." So a probe that only knows how to chat reports a working
# model as unavailable — which is exactly the error this module shipped with on 2026-10-11.
DECISIONS = "https://openrouter.ai/api/alpha/decisions"
DECISIONS_BODY = {
    "state": "probe",
    "questions": {"ok": {"type": "noul", "instructions": "Is this a probe?"}},
}
# The intended decision model, and the one that turned out to answer on the chat surface. Both are
# recorded because the first choice was named deliberately (ADR 0007) and a substitution has to be
# visible rather than silent.
WANTED = "microsoft/microsoft-decision-1"
FALLBACK = "typesafe/jev-router"
PROBE_PROMPT = 'Reply with exactly this JSON and nothing else: {"ok": true}'


class _NoKey(Exception):
    pass


def api_key() -> str:
    """The OpenRouter key pi uses. Read, never logged, never written anywhere."""
    import os
    if os.environ.get("OPENROUTER_API_KEY"):
        return os.environ["OPENROUTER_API_KEY"]
    auth = Path(os.path.expanduser("~/.pi/agent/auth.json"))
    if auth.exists():
        def walk(obj):
            if isinstance(obj, dict):
                for v in obj.values():
                    if isinstance(v, str) and v.startswith("sk-or-"):
                        return v
                    found = walk(v)
                    if found:
                        return found
            elif isinstance(obj, list):
                for v in obj:
                    found = walk(v)
                    if found:
                        return found
            return None
        try:
            key = walk(json.loads(auth.read_text(encoding="utf-8")))
        except Exception:
            key = None
        if key:
            return key
    raise _NoKey("no OpenRouter key in OPENROUTER_API_KEY or ~/.pi/agent/auth.json")


def _get(url: str, timeout: int = 45) -> tuple[int, str]:
    req = urllib.request.Request(url, headers={"User-Agent": "rfp-bid-brief/provider-probe"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as res:
            return res.status, res.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", "replace")
    except Exception as exc:  # offline, DNS, TLS
        return 0, f"{type(exc).__name__}: {exc}"


def _call(model: str, prompt: str, timeout: int = 90) -> tuple[int, str]:
    """One minimal completion. This — not a metadata endpoint — is what callable means."""
    status, body = _post(COMPLETIONS, {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 32,
        "temperature": 0,
    }, timeout)
    if status == 400 and "decisions model" in body:
        # Not a failure: the wrong surface. Ask the decisions endpoint the same question, in the
        # schema decisions models actually take (TypeSafe System One: state + typed questions).
        payload = dict(DECISIONS_BODY)
        payload["model"] = model
        return _post(DECISIONS, payload, timeout)
    return status, body


def _post(url: str, payload: dict, timeout: int = 90) -> tuple[int, str]:
    try:
        key = api_key()
    except _NoKey as exc:
        return 0, f"{exc}"
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                 "User-Agent": "rfp-bid-brief/provider-probe"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as res:
            return res.status, res.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", "replace")
    except Exception as exc:
        return 0, f"{type(exc).__name__}: {exc}"


@dataclass
class Probe:
    model: str
    catalogue_status: int = 0
    catalogue_size: int = 0
    model_status: int = 0
    in_catalogue: bool = False
    call_status: int = 0
    call_body: str = ""
    entry: dict | None = None
    note: str = ""

    @property
    def callable_now(self) -> bool:
        return self.call_status == 200

    @property
    def surface(self) -> str:
        """Which endpoint answered: a chat model and a decision model are both callable, differently."""
        if not self.callable_now:
            return "—"
        return "decisions" if "answers" in self.call_body else "chat/completions"

    @property
    def answered(self) -> str:
        """What it actually said, trimmed. Evidence, not a boolean."""
        try:
            payload = json.loads(self.call_body)
            if "answers" in payload:
                asked = payload["answers"]
                rendered = ", ".join(f"{k}={json.dumps(v)}" for k, v in asked.items())
                resolved = payload.get("model") or self.model
                return f"{rendered}  (resolved: {resolved})"
            content = payload["choices"][0]["message"]["content"]
            return " ".join(str(content).split())[:120]
        except Exception:
            return " ".join(self.call_body.split())[:120]


def probe(model: str = WANTED, fetch: Callable[[str], tuple[int, str]] = _get,
          call: Callable[[str, str], tuple[int, str]] = _call) -> Probe:
    out = Probe(model=model)
    status, body = fetch(CATALOGUE)
    out.catalogue_status = status
    if status == 200:
        try:
            ids = [m["id"] for m in json.loads(body).get("data", [])]
            out.catalogue_size = len(ids)
            out.in_catalogue = model in ids
        except Exception as exc:
            out.note = f"catalogue unreadable: {exc}"
    else:
        out.note = f"catalogue unavailable (HTTP {status})"

    status, body = fetch(MODEL_URL.format(model=model))
    out.model_status = status
    if status == 200:
        try:
            payload = json.loads(body)
            out.entry = payload.get("data", payload)
        except Exception:
            out.entry = None

    out.call_status, out.call_body = call(model, PROBE_PROMPT)
    return out


def render(p: Probe) -> str:
    lines = [
        f"decision model: {p.model}",
        f"  catalogue      HTTP {p.catalogue_status}, {p.catalogue_size} models, "
        f"{'present' if p.in_catalogue else 'NOT present'}  (informational)",
        f"  model endpoint HTTP {p.model_status}  (informational)",
        f"  actual call    HTTP {p.call_status} on {p.surface}",
    ]
    if p.callable_now:
        lines.append(f"  answered       {p.answered}")
        lines.append("  callable now   YES — this is decided by making a call, not by asking a catalogue")
    else:
        lines.append(f"  error          {p.answered}")
        lines.append("  callable now   NO")
    if p.entry:
        for key in ("name", "context_length", "created"):
            if key in p.entry:
                lines.append(f"  {key:<14} {p.entry[key]}")
    if p.note:
        lines.append(f"  note           {p.note}")
    return "\n".join(lines)
