"""Baseline evaluation: does the decision layer reproduce the committed labels?

## Read this before quoting the number

The extractions fed to this are **hand-authored with knowledge of the labels**. So agreement here is
not evidence about extraction quality — it is a consistency check on the *decision layer and the
requirement vocabulary*: given a correct reading of each solicitation, do the bindings land on the
committed call and the committed reason class?

That is worth having. It means the vocabulary is expressive enough for all four reason classes, the
profile can drive all four, and a regression in a binding shows up as a failed test rather than as a
quiet change in published numbers. It does **not** mean the pipeline reads documents correctly, and
reporting it as if it did would be the same category of error as quoting an accuracy figure without
its conditions.

Two numbers are deliberately absent: precision/recall over classes with four positives in eleven
fixtures would be thin, and there is no probability to score yet — `decide` emits none, so the
pre-registered operating point is not exercised. Both arrive with the model-backed extractor and the
calibrated channel; the shape of the report arrives now.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from .decide import Decision
from .extract import Extraction


@dataclass
class Row:
    fixture: str
    truth_label: str
    truth_class: str
    predicted_label: str
    predicted_class: str
    reasons: int
    triggered: tuple[str, ...] = ()

    @property
    def label_ok(self) -> bool:
        return self.truth_label == self.predicted_label

    @property
    def class_ok(self) -> bool:
        return self.truth_class == self.predicted_class

    @property
    def truth_class_triggered(self) -> bool:
        """Did the layer account for the labelled reason class, even if it ranked another first?

        This separates two failures an exact-match metric conflates: missing the reason, versus
        agreeing on the reasons and disagreeing about which dominates.

        `in_scope` is the absence of a reason rather than a reason, so it is accounted for when
        nothing triggered. Reading it as membership would mark every correct bid as a miss.
        """
        if self.truth_class == "in_scope":
            return not self.triggered
        return self.truth_class in self.triggered


@dataclass
class Baseline:
    rows: list[Row] = field(default_factory=list)
    missing_extraction: list[str] = field(default_factory=list)
    missing_label: list[str] = field(default_factory=list)
    unusable: list[dict] = field(default_factory=list)

    @property
    def eligible(self) -> int:
        """Fixtures the decision layer could actually be run on — the denominator that matters."""
        return self.n

    @property
    def n(self) -> int:
        return len(self.rows)

    @property
    def label_agree(self) -> int:
        return sum(r.label_ok for r in self.rows)

    @property
    def class_agree(self) -> int:
        return sum(r.class_ok for r in self.rows)

    @property
    def class_found(self) -> int:
        return sum(r.truth_class_triggered for r in self.rows)

    @property
    def ranking_divergences(self) -> list[str]:
        return [r.fixture for r in self.rows if r.truth_class_triggered and not r.class_ok]

    def confusion(self) -> dict[str, dict[str, int]]:
        out: dict[str, dict[str, int]] = {}
        for r in self.rows:
            out.setdefault(r.truth_label, {}).setdefault(r.predicted_label, 0)
            out[r.truth_label][r.predicted_label] += 1
        return out

    def to_json(self) -> dict:
        return {
            "schema": "baseline/1",
            "what_this_measures": (
                "the decision layer and requirement vocabulary, against hand-authored extractions. "
                "NOT extraction quality: the extractions were written with knowledge of the labels."
            ),
            "not_yet_measurable": [
                "extraction accuracy — needs the model-backed extractor",
                "calibration and the operating point — decide() emits no probability yet",
                "precision/recall per class — four positives in eleven fixtures is too thin to report",
            ],
            "n": self.n,
            "label_agreement": f"{self.label_agree}/{self.n}",
            "reason_class_agreement": f"{self.class_agree}/{self.n}",
            "truth_class_found_or_correctly_absent": f"{self.class_found}/{self.n}",
            "ranking_divergences": self.ranking_divergences,
            "ranking_note": (
                "A divergence here means the layer triggered the labelled reason class and also "
                "triggered another, and the priority order (geography > product > functional > "
                "operations) put the other first. Two fixtures trigger geography AND operations, "
                "and their labels rank them in opposite directions, so no single priority order can "
                "reproduce both. Recorded rather than tuned."
            ),
            "confusion": self.confusion(),
            "rows": [
                {
                    "fixture": r.fixture,
                    "truth_label": r.truth_label,
                    "truth_reason_class": r.truth_class,
                    "predicted_label": r.predicted_label,
                    "predicted_reason_class": r.predicted_class,
                    "exclusions_matched": r.reasons,
                    "label_ok": r.label_ok,
                    "class_ok": r.class_ok,
                }
                for r in self.rows
            ],
            "missing_extraction": self.missing_extraction,
            "missing_label": self.missing_label,
            "unusable_extractions": self.unusable,
            "unusable_note": (
                "An extraction refused by the citation gate cannot produce a decision. That refusal "
                "is a measurement, not an error: for a model-backed extractor it is the "
                "citation-integrity rate, and a run that crashes on it reports nothing."
            ),
        }


def run(
    labels: dict,
    extraction_for: Callable[[str], Extraction | None],
    decide: Callable[[Extraction], Decision],
) -> Baseline:
    out = Baseline()
    for entry in labels["labels"]:
        fixture = entry["fixture"]
        ex = extraction_for(fixture)
        if ex is None:
            out.missing_extraction.append(fixture)
            continue
        decision = decide(ex)
        out.rows.append(
            Row(
                fixture=fixture,
                truth_label=entry["label"],
                truth_class=entry["reason_class"],
                predicted_label=decision.recommendation,
                predicted_class=decision.primary_reason_class,
                reasons=len(decision.reasons),
                triggered=tuple(sorted({r.reason_class for r in decision.reasons})),
            )
        )
    return out


@dataclass
class ComparisonRow:
    fixture: str
    identical: bool
    differing: int
    details: list[str]
    req_total: int = 0
    req_differing: int = 0

    @property
    def requirements_agree(self) -> bool:
        return self.req_differing == 0 and self.req_total > 0


def compare_extractions(dir_a: Path, dir_b: Path) -> list[ComparisonRow]:
    """Field-level agreement between two extraction sets, over the fixtures they share.

    Requirements are separated from facts because only the requirements are a contracted task: the
    prompt names the five requirement kinds and two facts, so a producer that omits `term` has not
    failed anything — it was never asked. Facts are reported as differences in wording and coverage,
    which is information about the two producers rather than a score.
    """
    rows: list[ComparisonRow] = []
    for fa in sorted(Path(dir_a).glob("*.json")):
        fb = Path(dir_b) / fa.name
        if not fb.exists():
            continue
        a = json.loads(fa.read_text(encoding="utf-8"))
        b = json.loads(fb.read_text(encoding="utf-8"))
        details: list[str] = []
        reqs_a, reqs_b = a.get("requirements", {}), b.get("requirements", {})
        req_keys = sorted(set(reqs_a) | set(reqs_b))
        req_differing = 0
        for key in req_keys:
            va = reqs_a.get(key, {}).get("value", "<missing>")
            vb = reqs_b.get(key, {}).get("value", "<missing>")
            if va != vb:
                req_differing += 1
                details.append(f"requirements.{key}: {va!r} vs {vb!r}")
        facts_a, facts_b = a.get("facts", {}), b.get("facts", {})
        for key in sorted(set(facts_a) | set(facts_b)):
            va = facts_a.get(key, {}).get("value", "<missing>")
            vb = facts_b.get(key, {}).get("value", "<missing>")
            if va != vb:
                details.append(f"facts.{key}: {va!r} vs {vb!r}")
        ca = sum(len(v.get("citations", [])) for g in ("facts", "requirements")
                 for v in a.get(g, {}).values())
        cb = sum(len(v.get("citations", [])) for g in ("facts", "requirements")
                 for v in b.get(g, {}).values())
        if ca != cb:
            details.append(f"citations: {ca} vs {cb}")
        rows.append(ComparisonRow(fa.stem, not details, len(details), details,
                                  len(req_keys), req_differing))
    return rows


def render(baseline: Baseline) -> str:
    lines = [
        "| fixture | truth | predicted | truth class | predicted class | ok |",
        "|---|---|---|---|---|---|",
    ]
    for r in sorted(baseline.rows, key=lambda x: (not x.label_ok, x.fixture)):
        mark = "✓" if r.label_ok and r.class_ok else ("~" if r.label_ok else "✗")
        lines.append(
            f"| {r.fixture[:46]} | {r.truth_label} | {r.predicted_label} | "
            f"{r.truth_class} | {r.predicted_class} | {mark} |"
        )
    cm = baseline.confusion()
    lines += [
        "",
        f"label agreement: {baseline.label_agree}/{baseline.n} · "
        f"reason-class agreement (primary): {baseline.class_agree}/{baseline.n} · "
        f"labelled reason class accounted for: {baseline.class_found}/{baseline.n}",
    ]
    if baseline.ranking_divergences:
        lines += [
            "",
            "ranking divergences (reason found, ranked below another): "
            + ", ".join(baseline.ranking_divergences),
        ]
    lines += [
        "",
        "| truth \\ predicted | " + " | ".join(sorted({p for d in cm.values() for p in d})) + " |",
        "|---|" + "---|" * len({p for d in cm.values() for p in d}),
    ]
    preds = sorted({p for d in cm.values() for p in d})
    for truth in sorted(cm):
        lines.append(f"| {truth} | " + " | ".join(str(cm[truth].get(p, 0)) for p in preds) + " |")
    if baseline.missing_extraction:
        lines += ["", f"no extraction yet: {', '.join(baseline.missing_extraction)}"]
    if baseline.unusable:
        lines += ["", f"refused by the citation gate ({len(baseline.unusable)}):"]
        for entry in baseline.unusable:
            first = entry["problems"][0] if entry["problems"] else "unknown"
            lines.append(f"- {entry['fixture']}: {first[:150]}")
    return "\n".join(lines)
