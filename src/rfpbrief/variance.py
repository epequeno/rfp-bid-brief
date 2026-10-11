"""Variance across repeated runs: the number this pipeline cannot yet quote without a spread.

Two passes with the same prompt and the same fixtures gave first-attempt cleanliness of 8/11 and
5/11. A single figure from a process that unstable is not a rate, and reporting one would be the
same error as quoting accuracy without its conditions. So repeated runs are recorded, and what gets
reported is a range with per-fixture stability rather than a headline.

An extraction that needed its repair attempt is a *different outcome* from one that was clean first
time, which is why outcomes are three-valued here — clean, repaired, refused — rather than
pass/fail. Collapsing repaired into clean would hide exactly the thing being measured.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

CLEAN = "clean"
REPAIRED = "repaired"
REFUSED = "refused"


@dataclass
class RunOutcome:
    run: str
    clean: list[str] = field(default_factory=list)
    repaired: list[str] = field(default_factory=list)
    refused: list[str] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.clean) + len(self.repaired) + len(self.refused)

    def outcome_for(self, fixture: str) -> str:
        if fixture in self.clean:
            return CLEAN
        if fixture in self.repaired:
            return REPAIRED
        return REFUSED

    def to_json(self) -> dict:
        return {
            "run": self.run,
            "clean": len(self.clean),
            "repaired": len(self.repaired),
            "refused": len(self.refused),
            "total": self.total,
        }


def read_run(directory: Path, label: str | None = None) -> RunOutcome:
    """Classify one run directory: which fixtures were clean, repaired, or refused."""
    directory = Path(directory)
    outcome = RunOutcome(run=label or directory.name)
    for path in sorted(directory.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        attempts = data.get("extractor", {}).get("attempts", 1)
        fixture = data.get("fixture", path.stem)
        (outcome.repaired if attempts > 1 else outcome.clean).append(fixture)
    refused_dir = directory / "_refused"
    if refused_dir.exists():
        for path in sorted(refused_dir.glob("*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            outcome.refused.append(data.get("fixture", path.stem))
    return outcome


@dataclass
class Variance:
    runs: list[RunOutcome] = field(default_factory=list)

    @property
    def fixtures(self) -> list[str]:
        seen: list[str] = []
        for run in self.runs:
            for f in (*run.clean, *run.repaired, *run.refused):
                if f not in seen:
                    seen.append(f)
        return sorted(seen)

    @property
    def clean_range(self) -> tuple[int, int]:
        counts = [len(r.clean) for r in self.runs]
        return (min(counts), max(counts)) if counts else (0, 0)

    def stability(self, fixture: str) -> str:
        """Was this fixture's outcome the same every run? Reported per fixture, not averaged away."""
        outcomes = {run.outcome_for(fixture) for run in self.runs}
        if len(outcomes) == 1:
            return next(iter(outcomes))
        return "varies"

    def to_json(self) -> dict:
        stable = {"clean": 0, "repaired": 0, "refused": 0, "varies": 0}
        for f in self.fixtures:
            stable[self.stability(f)] += 1
        return {
            "schema": "variance/1",
            "what_this_measures": (
                "outcome stability across repeated identical runs. A single pass is not a rate: two "
                "runs of this pipeline gave 8/11 and 5/11 first-attempt cleanliness."
            ),
            "runs": [r.to_json() for r in self.runs],
            "clean_first_attempt": {
                "per_run": [len(r.clean) for r in self.runs],
                "min": self.clean_range[0],
                "max": self.clean_range[1],
                "usable_after_repair": [r.total - len(r.refused) for r in self.runs],
            },
            "per_fixture_stability": {f: self.stability(f) for f in self.fixtures},
            "stability_counts": stable,
            "note": (
                "`varies` is the headline: those fixtures cannot be described by a single pass. "
                "Pinning temperature or seed would collapse it, at the cost of measuring a different "
                "configuration than the one in use."
            ),
        }


def summarise(runs: list[RunOutcome]) -> Variance:
    return Variance(runs=list(runs))


def render(variance: Variance) -> str:
    lines = ["| run | clean first attempt | repaired | refused | usable |", "|---|---|---|---|---|"]
    for r in variance.runs:
        lines.append(f"| {r.run} | {len(r.clean)} | {len(r.repaired)} | {len(r.refused)} | {r.total - len(r.refused)} |")
    lo, hi = variance.clean_range
    lines += [
        "",
        f"clean first attempt across {len(variance.runs)} runs: **{lo}–{hi}** of {variance.runs[0].total}",
        "",
        "| fixture | stability |",
        "|---|---|",
    ]
    for f in variance.fixtures:
        lines.append(f"| {f[:58]} | {variance.stability(f)} |")
    return "\n".join(lines)
