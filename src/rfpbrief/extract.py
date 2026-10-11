"""Extraction: typed values that carry the span they came from.

The *source* of an extraction is swappable — a hand-authored file today, a model calling a typed
decision layer later — but its *contract* is not. Every value carries at least one citation, and a
citation that does not locate in the span index is a **load error**, not a warning.

That is why this module has no partial-success mode: `load()` either returns an extraction in which
every citation has been checked against the fixture, or it raises with the list of failures. A
pipeline that can carry an unverifiable citation is a pipeline whose briefs cannot be trusted, and
the cheapest place to refuse is here.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .spans import Document

EXTRACTIONS = Path(__file__).resolve().parents[2] / "extractions"


class ExtractionError(Exception):
    """Raised when an extraction cannot be trusted. Carries every problem, not just the first."""

    def __init__(self, problems: list[str]) -> None:
        self.problems = problems
        super().__init__("; ".join(problems))


@dataclass(frozen=True)
class Citation:
    span_id: str
    page: int
    quote: str

    def render(self) -> str:
        return f'"{self.quote}" (page {self.page}, {self.span_id})'

    def to_json(self) -> dict:
        return {"span_id": self.span_id, "page": self.page, "quote": self.quote}


@dataclass(frozen=True)
class Fact:
    name: str
    value: Any
    citations: tuple[Citation, ...]
    kind: str = "string"


@dataclass
class Extraction:
    fixture: str
    produced_by: str
    facts: dict[str, Fact] = field(default_factory=dict)
    requirements: dict[str, Fact] = field(default_factory=dict)

    def citations(self) -> list[Citation]:
        return [c for f in (*self.facts.values(), *self.requirements.values()) for c in f.citations]


def _citations(raw: list[dict]) -> tuple[Citation, ...]:
    return tuple(Citation(span_id=c["span_id"], page=c["page"], quote=c["quote"]) for c in raw)


def validate(doc: Document, data: dict) -> list[str]:
    """Every reason this extraction cannot be trusted. Empty means trustworthy."""
    problems: list[str] = []
    if data.get("fixture") != doc.fixture:
        problems.append(f"fixture mismatch: extraction says {data.get('fixture')!r}, "
                        f"document is {doc.fixture!r}")
    groups = {"facts": data.get("facts", {}), "requirements": data.get("requirements", {})}
    for group, entries in groups.items():
        for name, entry in entries.items():
            cites = entry.get("citations") or []
            if not cites:
                problems.append(f"{group}.{name}: no citation — an uncited field is unusable")
                continue
            for c in cites:
                span_id, page, quote = c.get("span_id"), c.get("page"), c.get("quote")
                if not span_id or not quote:
                    problems.append(f"{group}.{name}: citation missing span_id or quote")
                    continue
                span = doc.span(span_id)
                if span is None:
                    problems.append(f"{group}.{name}: span {span_id!r} does not exist in {doc.fixture}")
                    continue
                if span.page != page:
                    problems.append(
                        f"{group}.{name}: citation says page {page}, span {span_id} is on page {span.page}"
                    )
                if not doc.validate_citation(span_id, quote):
                    elsewhere = doc.locate(quote)
                    hint = ""
                    if elsewhere:
                        homes = ", ".join(sorted({c.id for c in elsewhere}))
                        hint = (f" [this quote does appear in {homes} — the citation names "
                                f"{span_id}. A quote that runs across a span boundary has to name "
                                f"one span and quote only the part inside it.]")
                    problems.append(
                        f"{group}.{name}: quote not found in span {span_id} under the verbatim rule: "
                        f"{quote[:70]!r}{hint}"
                    )
    return problems


def load(path: Path, doc: Document) -> Extraction:
    """Load and validate. Raises ExtractionError listing every problem found."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    problems = validate(doc, data)
    if problems:
        raise ExtractionError(problems)
    ex = Extraction(fixture=data["fixture"], produced_by=data.get("produced_by", "unknown"))
    for group, target in (("facts", ex.facts), ("requirements", ex.requirements)):
        for name, entry in data.get(group, {}).items():
            target[name] = Fact(
                name=name,
                value=entry.get("value"),
                citations=_citations(entry.get("citations", [])),
                kind=entry.get("kind", "string"),
            )
    return ex


def for_fixture(doc: Document, extractions_dir: Path | None = None) -> Extraction:
    """The committed extraction for a fixture, by stem."""
    directory = Path(extractions_dir) if extractions_dir else EXTRACTIONS
    path = directory / f"{Path(doc.fixture).stem}.json"
    if not path.exists():
        raise FileNotFoundError(
            f"no extraction for {doc.fixture}: expected {path.relative_to(path.parents[1])}. "
            f"A fixture without an extraction cannot be briefed."
        )
    return load(path, doc)
