"""Is the decision model we want callable *today*? A probe, not a recollection.

The intended probability channel is a decision-scoring model (ADR 0007), and the one we want is
listed by the provider but was not served by its API on 2026-10-11: the catalogue has 458 models and
none of them is it, and the per-model endpoint answers 404 with and without a key.

That is the kind of fact that goes stale silently, in both directions — a listing can appear before
an API serves it, and an API can serve a model a catalogue has not listed yet. So it is probed rather
than remembered, and the probe is cheap enough to run any time the question comes up.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Callable

CATALOGUE = "https://openrouter.ai/api/v1/models"
MODEL_URL = "https://openrouter.ai/api/v1/models/{model}"
WANTED = "microsoft/microsoft-decision-1"


def _get(url: str, timeout: int = 45) -> tuple[int, str]:
    req = urllib.request.Request(url, headers={"User-Agent": "rfp-bid-brief/provider-probe"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as res:
            return res.status, res.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", "replace")
    except Exception as exc:  # offline, DNS, TLS
        return 0, f"{type(exc).__name__}: {exc}"


@dataclass
class Probe:
    model: str
    catalogue_status: int = 0
    catalogue_size: int = 0
    model_status: int = 0
    in_catalogue: bool = False
    entry: dict | None = None
    note: str = ""

    @property
    def callable_now(self) -> bool:
        return self.model_status == 200


def probe(model: str = WANTED, fetch: Callable[[str], tuple[int, str]] = _get) -> Probe:
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
    return out


def render(p: Probe) -> str:
    lines = [
        f"decision model: {p.model}",
        f"  catalogue      HTTP {p.catalogue_status}, {p.catalogue_size} models, "
        f"{'present' if p.in_catalogue else 'NOT present'}",
        f"  model endpoint HTTP {p.model_status}",
        f"  callable now   {'yes' if p.callable_now else 'NO'}",
    ]
    if p.entry:
        for key in ("name", "context_length", "created"):
            if key in p.entry:
                lines.append(f"  {key:<14} {p.entry[key]}")
    if not p.callable_now:
        lines.append("  what this means: the listing exists, the API does not serve it yet. "
                     "Nothing in this repository may depend on it until it does — see ADR 0007.")
    if p.note:
        lines.append(f"  note           {p.note}")
    return "\n".join(lines)
