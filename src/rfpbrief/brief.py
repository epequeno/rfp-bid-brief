"""The brief: one page, every claim traceable to a span.

Rendering is a pure function of a `Decision`, a validated `Extraction` and the `Document` they were
checked against. There is no model call in this module, so what a reader sees is exactly what the
pipeline decided plus exactly what the fixture says — and the quotes are taken from the span index
rather than reproduced from memory.

The closing line is not decoration. Every quote in a brief has been located in its fixture by
`spans.Document.validate_citation` at load time, so a brief that exists at all is one whose
citations resolved. The alternative — a brief that renders first and is checked later — is how a
fabricated quotation reaches a reader with a page number attached.
"""

from __future__ import annotations

from .decide import BID, Decision
from .extract import Citation, Extraction
from .spans import Document

TITLE_OF = {
    "bid": "BID",
    "no_bid": "NO-BID",
}

CLASS_TITLE = {
    "geography": "Geography",
    "product_not_services": "Buying a product, not services",
    "functional_stack_not_held": "Functional stack not held",
    "operations_not_projects": "Operations, not a project",
    "in_scope": "In scope",
}


def _citation_line(c: Citation) -> str:
    return f'"{c.quote}" (page {c.page}, span `{c.span_id}`)'


def render(decision: Decision, extraction: Extraction, doc: Document) -> str:
    subject = extraction.facts.get("subject")
    issuer = extraction.facts.get("issuer")
    title = subject.value if subject else doc.fixture
    who = issuer.value if issuer else "unknown issuer"

    out: list[str] = []
    out.append(f"# {title}")
    out.append("")
    out.append(f"**{who}** · recommendation: **{TITLE_OF[decision.recommendation]}**")
    out.append("")
    out.append(f"Primary reason class: **{CLASS_TITLE.get(decision.primary_reason_class, decision.primary_reason_class)}**")
    out.append("")
    for note in decision.notes:
        out.append(f"> {note}")
    out.append("")

    if decision.recommendation == BID:
        out.append("## Why")
        out.append("")
        out.append("No exclusion in the bidder profile is triggered by this solicitation.")
        if decision.considered:
            out.append("")
            out.append("Requirements the profile was checked against and does **not** exclude:")
            out.append("")
            for c in decision.considered:
                cites = "; ".join(_citation_line(x) for x in c.citations)
                out.append(f"- `{c.requirement}` = {c.value!r} — {cites}")
    else:
        out.append("## Why not")
        out.append("")
        for i, reason in enumerate(decision.reasons, start=1):
            out.append(f"**{i}. {CLASS_TITLE.get(reason.reason_class, reason.reason_class)}** — {reason.summary}.")
            out.append("")
            out.append(f"- the profile excludes *{reason.profile_exclusion}*")
            for c in reason.citations:
                out.append(f"- the fixture says {_citation_line(c)}")
            out.append("")

    out.append("## Extracted facts")
    out.append("")
    out.append("| field | value | source |")
    out.append("|---|---|---|")
    for name, fact in extraction.facts.items():
        cites = "; ".join(f"p{c.page} `{c.span_id}`" for c in fact.citations)
        out.append(f"| {name} | {fact.value} | {cites} |")
    out.append("")

    out.append("## Citations")
    out.append("")
    seen: set[str] = set()
    for c in extraction.citations():
        key = f"{c.span_id}:{c.quote}"
        if key in seen:
            continue
        seen.add(key)
        out.append(f"- {_citation_line(c)}")
    out.append("")
    out.append(
        "---\n"
        f"_Every quote above was located in `{doc.fixture}` at build time under the verbatim rule "
        "(whitespace-insensitive, word-boundary-aligned, everything else exact). A quote that does "
        "not resolve fails the build rather than reaching a reader. Fixture sha256 "
        f"`{doc.fixture_sha256[:16]}…`, span index built with {doc.engine_version}._"
    )
    out.append("")
    return "\n".join(out)
