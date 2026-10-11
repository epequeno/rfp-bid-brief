"""Span indexing — the module every downstream claim rests on.

ADR 0001 says each extracted field cites a span, and that a quoted span must exist **verbatim** in
its fixture. That guarantee is only as good as this module, so it has exactly two properties to
defend, and both are tested:

* **determinism** — the same fixture yields the same text, spans and ids on every run;
* **reachability** — every span's offsets index into the stored page text, so a span can be
  re-derived rather than trusted.

## What "verbatim" means here

PDF text arrives wrapped, column-artefacted and padded. A quote a human would copy can therefore
never match the raw extraction, and pretending otherwise is how citation checks become theatre. So
this module states the rule precisely instead.

A **span** is a sentence-ish unit of a page, and it is the *locator*: it has a stable id, a page and
offsets into the stored page text. A **citation** is a span plus a quote, and the rule is:

    a quote is valid  ⇔  collapse_ws(quote) occurs in collapse_ws(span.text) **at word boundaries**

Whitespace is the **only** thing normalised. Punctuation, case, hyphenation, digits and symbols must
match exactly. Unicode text is normalised to NFC when the document is built; no other transform is
applied.

The word-boundary condition is not decoration. Plain substring containment accepts `four (4) hour`
as a prefix of `four (4) hours`, so a truncated quote would pass verification and then read as a
typo in the brief. Requiring both ends of the match to sit at a boundary rejects that while keeping
the whitespace tolerance that line wrapping makes necessary.

The containment form was chosen during the first spike, having first been implemented as equality.
Equality is unusable in practice: the Tahoe fixture's disqualifying requirement reads *"In case of
an emergency, be on-site within four (4) hours"*, and a brief that may only quote the whole sentence
cannot quote the four hours. Equality is still available — `find()` — because an exact whole-span
match is a useful primitive; `locate()` is what citations use.

The extraction engine is pinned by name and version in the index, because the text this module
produces is a function of that engine and not only of the PDF.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import unicodedata
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

ENGINE = "pdftotext"
PAGE_SEPARATOR = "\f"

# Sentence ends. Deliberately conservative: a split is only taken at [.!?;] followed by whitespace,
# and then vetoed if the token before it is a known abbreviation. Over-splitting is harmless here
# (spans are citation units, not semantic ones); under-splitting is worse, because a citation that
# spans twenty sentences is unusable in a brief. Long spans are therefore cut at a clause boundary.
_SENTENCE_BREAK = re.compile(r"(?<=[.!?;])\s+")
_ABBREVIATIONS = {
    "no", "nos", "inc", "ltd", "co", "corp", "llc", "plc", "dept", "div", "comm", "admin",
    "mr", "mrs", "ms", "dr", "prof", "sr", "jr", "st", "mt", "ft", "vs", "etc", "fig", "figs",
    "sec", "secs", "art", "para", "para", "pp", "ed", "vol", "approx", "est", "min", "max",
    "eg", "ie", "cf", "al", "ca", "usa", "us", "u.s", "u.s.a", "d.c", "ph.d", "a.m", "p.m",
}
_MAX_SPAN_CHARS = 320
_CLAUSE_BREAK = re.compile(r"(?<=[,;:])\s+")
_WS = re.compile(r"\s+")


def collapse_ws(s: str) -> str:
    """The one normalisation that citation matching is allowed to perform."""
    return _WS.sub(" ", s).strip()


def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


@lru_cache(maxsize=1)
def engine_version() -> str:
    try:
        out = subprocess.run(
            [ENGINE, "-v"], capture_output=True, text=True, timeout=30
        )
        return (out.stdout + out.stderr).splitlines()[0].strip()
    except Exception as exc:  # pragma: no cover - environment probe
        return f"unknown ({exc})"


def extract_pages(path: Path) -> list[str]:
    """Run the engine and split its output into pages. No parsing, no interpretation."""
    res = subprocess.run(
        [ENGINE, "-q", "-enc", "UTF-8", str(path), "-"],
        capture_output=True,
        timeout=300,
    )
    if res.returncode != 0:
        raise RuntimeError(
            f"{ENGINE} failed on {path.name}: {res.stderr.decode('utf-8', 'replace')[:300]}"
        )
    raw = res.stdout.decode("utf-8", "replace")
    return raw.split(PAGE_SEPARATOR)


def _clean_page(raw: str) -> str:
    """NFC, strip trailing padding per line, and keep paragraph breaks.

    Paragraph structure is preserved because the extractor benefits from it, while *matching* is
    whitespace-insensitive (see `collapse_ws`). Line wrapping is NOT undone: hyphenation is left
    exactly as the document has it, since repairing it requires guessing, and guessing is how a
    citation check starts passing on text that was never there.
    """
    text = unicodedata.normalize("NFC", raw)
    lines = [line.rstrip() for line in text.splitlines()]
    out: list[str] = []
    blank = False
    for line in lines:
        if line.strip():
            out.append(line)
            blank = False
        elif not blank:
            out.append("")
            blank = True
    return "\n".join(out).strip("\n")


def _split_spans(page_text: str, page_no: int) -> list["Span"]:
    spans: list[Span] = []
    ordinal = 0
    cursor = 0
    for piece in _split_pieces(page_text):
        if not piece.strip():
            continue
        start = page_text.index(piece, cursor)
        end = start + len(piece)
        cursor = end
        spans.append(
            Span(
                id=f"p{page_no}-s{ordinal}",
                page=page_no,
                start=start,
                end=end,
                text=piece,
            )
        )
        ordinal += 1
    return spans


def _ends_with_abbreviation(before: str) -> bool:
    """True if the text before a candidate break ends in a known abbreviation.

    Without this, "Section 4. No. 3 applies." splits mid-thought at every period. The list is
    deliberately small and local to solicitation prose — a wrong entry here only costs span
    granularity, never correctness, because matching is exact.
    """
    token = before.split()[-1] if before.split() else ""
    key = token.rstrip(".,;:").lower()
    return key in _ABBREVIATIONS or token.lower() in _ABBREVIATIONS


def _split_pieces(page_text: str) -> list[str]:
    """Sentence-ish units, clause-cut when a unit runs long. Preserves the exact original text."""
    raw: list[str] = []
    start = 0
    for m in _SENTENCE_BREAK.finditer(page_text):
        if _ends_with_abbreviation(page_text[: m.start()]):
            continue
        raw.append(page_text[start : m.start() + 1])
        start = m.end()
    raw.append(page_text[start:])

    pieces: list[str] = []
    for chunk in raw:
        pieces.extend(_cut_long(chunk))
    return [p for p in pieces if p.strip()]


def _cut_long(chunk: str) -> list[str]:
    """Cut an over-long chunk at the clause break nearest the budget, falling back to a word break."""
    out: list[str] = []
    rest = chunk
    while len(rest) > _MAX_SPAN_CHARS:
        cut = 0
        for m in _CLAUSE_BREAK.finditer(rest):
            if m.end() <= _MAX_SPAN_CHARS:
                cut = m.end()
            else:
                break
        if cut == 0:
            cut = rest.rfind(" ", 0, _MAX_SPAN_CHARS)
            if cut <= 0:
                break
        out.append(rest[:cut])
        rest = rest[cut:]
    if rest:
        out.append(rest)
    return out


@dataclass(frozen=True)
class Span:
    id: str
    page: int
    start: int
    end: int
    text: str

    @property
    def quote(self) -> str:
        """The rendering used in a brief and in matching. Never the raw slice."""
        return collapse_ws(self.text)

    def to_json(self) -> dict:
        return {"id": self.id, "page": self.page, "start": self.start, "end": self.end,
                "chars": len(self.text), "text": self.text}


@dataclass(frozen=True)
class Page:
    number: int
    text: str

    @property
    def sha256(self) -> str:
        return sha256_text(self.text)

    def to_json(self) -> dict:
        return {"number": self.number, "sha256": self.sha256, "chars": len(self.text)}


@dataclass
class Document:
    fixture: str
    fixture_sha256: str
    engine: str
    engine_version: str
    pages: list[Page]
    spans: list[Span]
    hyphen_breaks: int = 0
    meta: dict = field(default_factory=dict)

    @property
    def text(self) -> str:
        """The whole document as stored, pages joined by a form feed sentinel."""
        return PAGE_SEPARATOR.join(p.text for p in self.pages)

    def span(self, span_id: str) -> Span | None:
        for s in self.spans:
            if s.id == span_id:
                return s
        return None

    def validate_citation(self, span_id: str, quote: str) -> bool:
        """Does `quote` sit inside span `span_id` under the verbatim rule?

        This is the check a citation has to pass. It is stricter than `find()` (which wants the
        whole span) and more precise than `locate()` (which answers "which spans could this be?"):
        the caller has already committed to a span, and this says whether that commitment holds.
        """
        span = self.span(span_id)
        return bool(span) and _contains_at_word_boundaries(span.quote, collapse_ws(quote))

    def find(self, quote: str) -> list[Span]:
        """Spans whose text *equals* the quote under the verbatim rule. The strict primitive."""
        target = collapse_ws(quote)
        return [s for s in self.spans if s.quote == target]

    def locate(self, quote: str, page: int | None = None) -> list["Citation"]:
        """Every (span, quote) pair where the quote sits *inside* a span, at word boundaries.

        `page` narrows the search when a quote is short enough to appear in several places; a
        caller that gets two hits for a page-unqualified quote has an ambiguous citation and must
        say which page it meant rather than pick one.
        """
        target = collapse_ws(quote)
        if not target:
            return []
        return [
            Citation(span=s, quote=target, page=s.page)
            for s in self.spans
            if (page is None or s.page == page) and _contains_at_word_boundaries(s.quote, target)
        ]

    def to_json(self) -> dict:
        return {
            "schema": "span-index/1",
            "fixture": self.fixture,
            "fixture_sha256": self.fixture_sha256,
            "engine": self.engine,
            "engine_version": self.engine_version,
            "normalisation": "NFC; per-line rstrip; paragraph breaks preserved; matching collapses "
                             "whitespace only",
            "pages": [p.to_json() for p in self.pages],
            "span_count": len(self.spans),
            "hyphenated_line_breaks": self.hyphen_breaks,
            "spans": [s.to_json() for s in self.spans],
            "meta": self.meta,
        }

    @classmethod
    def from_json(cls, data: dict) -> "Document":
        return cls(
            fixture=data["fixture"],
            fixture_sha256=data["fixture_sha256"],
            engine=data["engine"],
            engine_version=data["engine_version"],
            pages=[Page(number=p["number"], text=p.get("text", "")) for p in data["pages"]],
            spans=[
                Span(id=s["id"], page=s["page"], start=s["start"], end=s["end"], text=s["text"])
                for s in data["spans"]
            ],
            hyphen_breaks=data.get("hyphenated_line_breaks", 0),
            meta=data.get("meta", {}),
        )


@dataclass(frozen=True)
class Citation:
    """A quote and the span that locates it. The unit every downstream claim is built from."""

    span: Span
    quote: str
    page: int

    @property
    def id(self) -> str:
        return self.span.id

    def to_json(self) -> dict:
        return {"span_id": self.span.id, "page": self.page, "quote": self.quote}


def _contains_at_word_boundaries(haystack: str, needle: str) -> bool:
    """Containment that refuses to match inside a word.

    `'four (4) hour' in 'four (4) hours'` is true and must not be: a citation may not truncate a
    word. Both ends of the match must be adjacent to a non-alphanumeric character or an end of text.
    """
    start = haystack.find(needle)
    while start != -1:
        end = start + len(needle)
        left_ok = start == 0 or not haystack[start - 1].isalnum()
        right_ok = end == len(haystack) or not haystack[end].isalnum()
        if left_ok and right_ok:
            return True
        start = haystack.find(needle, start + 1)
    return False


def _count_hyphen_breaks(text: str) -> int:
    """Line-end hyphens: the one artefact this module refuses to repair, so it is counted instead."""
    return len(re.findall(r"[A-Za-z]-\n[a-z]", text))


def build(path: Path, fixture_name: str | None = None) -> Document:
    """Parse a fixture into a span-indexed document. Deterministic; no model involved."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)
    pages: list[Page] = []
    spans: list[Span] = []
    for i, raw in enumerate(extract_pages(path), start=1):
        text = _clean_page(raw)
        if not text:
            continue
        page = Page(number=i, text=text)
        pages.append(page)
        spans.extend(_split_spans(text, i))
    flat = PAGE_SEPARATOR.join(p.text for p in pages)
    return Document(
        fixture=fixture_name or path.name,
        fixture_sha256=sha256_file(path),
        engine=ENGINE,
        engine_version=engine_version(),
        pages=pages,
        spans=spans,
        hyphen_breaks=_count_hyphen_breaks(flat),
        meta={"source_path_kind": "fixtures/", "page_count": len(pages)},
    )


def write_index(doc: Document, out: Path) -> Path:
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc.to_json(), indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return out


def read_index(path: Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def reproducibility_report(doc: Document, index: dict) -> list[str]:
    """Compare a freshly built document against a committed index. Returns a list of differences."""
    problems: list[str] = []
    if index.get("fixture_sha256") != doc.fixture_sha256:
        problems.append(
            f"fixture changed: index has {index.get('fixture_sha256', '?')[:16]}…, "
            f"fixture is {doc.fixture_sha256[:16]}…"
        )
    if index.get("engine_version") != doc.engine_version:
        problems.append(
            f"engine changed: index built with {index.get('engine_version')!r}, "
            f"this build used {doc.engine_version!r}"
        )
    if index.get("span_count") != len(doc.spans):
        problems.append(f"span count: index {index.get('span_count')}, rebuilt {len(doc.spans)}")
    old_pages = {p["number"]: p["sha256"] for p in index.get("pages", [])}
    new_pages = {p.number: p.sha256 for p in doc.pages}
    if old_pages != new_pages:
        differing = sorted(set(old_pages) ^ set(new_pages)) or [
            n for n in old_pages if old_pages[n] != new_pages.get(n)
        ]
        problems.append(f"page text differs on page(s) {differing}")
    return problems
