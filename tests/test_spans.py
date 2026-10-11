"""Tests for the span index — the properties ADR 0001 depends on.

Offline and model-free: parsing is arithmetic on a PDF, and every test here runs without a network
call or an API key.
"""

from __future__ import annotations

import json

import pytest

from rfpbrief import parse as cli
from rfpbrief import spans

TAHOE = "tahoe-transportation-district-it-consulting-2025.pdf"
ON_SITE_QUOTE = "be on-site within four (4) hours"


@pytest.fixture(scope="module")
def tahoe() -> spans.Document:
    return spans.build(cli.FIXTURES / TAHOE, fixture_name=TAHOE)


def test_offsets_index_into_the_page_text(tahoe: spans.Document) -> None:
    """Reachability: every span is exactly the slice of stored page text it claims to be."""
    by_page = {p.number: p.text for p in tahoe.pages}
    for s in tahoe.spans:
        assert by_page[s.page][s.start : s.end] == s.text, s.id


def test_spans_are_ordered_and_do_not_overlap(tahoe: spans.Document) -> None:
    last_page, last_end = 0, -1
    for s in tahoe.spans:
        if s.page == last_page:
            assert s.start >= last_end, f"{s.id} overlaps the previous span"
        else:
            assert s.page > last_page
            last_page, last_end = s.page, -1
        last_end = s.end


def test_span_ids_are_unique(tahoe: spans.Document) -> None:
    ids = [s.id for s in tahoe.spans]
    assert len(ids) == len(set(ids))


def test_page_text_covers_every_span_character(tahoe: spans.Document) -> None:
    for page in tahoe.pages:
        covered = sum(s.end - s.start for s in tahoe.spans if s.page == page.number)
        # Whitespace between spans is expected to be uncovered; nothing else should be missing.
        assert covered <= len(page.text)
        assert covered >= len(page.text) * 0.75, f"page {page.number} is mostly uncovered text"


def test_determinism(tahoe: spans.Document) -> None:
    """The same fixture yields byte-identical JSON on a second build."""
    again = spans.build(cli.FIXTURES / TAHOE, fixture_name=TAHOE)
    assert json.dumps(again.to_json(), sort_keys=True) == json.dumps(tahoe.to_json(), sort_keys=True)


def test_known_quote_locates_exactly_one_citation(tahoe: spans.Document) -> None:
    """The disqualifying requirement in this fixture must resolve to one span, unambiguously."""
    found = tahoe.locate(ON_SITE_QUOTE)
    assert len(found) == 1, [(c.id, c.page) for c in found]
    assert ON_SITE_QUOTE in found[0].quote


def test_verbatim_rule_tolerates_whitespace_only(tahoe: spans.Document) -> None:
    """A quote copied across a line wrap still matches — this is the whole reason for the rule."""
    wrapped = "be on-site\n  within four (4)   hours"
    assert tahoe.locate(wrapped), "whitespace differences must not break a match"


def test_verbatim_rule_is_not_lenient_about_anything_else(tahoe: spans.Document) -> None:
    """Digits, punctuation and wording must match exactly. A near-miss is not a citation."""
    for wrong in (
        "be on-site within four (4) hour",       # plural dropped
        "be onsite within four (4) hours",       # hyphen dropped — the tolerant-looking case
        "be on-site within 4 hours",             # digits reformatted
        "be on-site within four (4) hours please",
        "BE ON-SITE WITHIN FOUR (4) HOURS",      # case is not normalised either
    ):
        assert not tahoe.locate(wrong), wrong


def test_exact_span_equality_is_stricter_than_containment(tahoe: spans.Document) -> None:
    """Why the contract is containment: equality cannot quote part of a sentence."""
    assert tahoe.find(ON_SITE_QUOTE) == [], "this quote is inside a span, not a whole span"
    span = tahoe.locate(ON_SITE_QUOTE)[0].span
    assert [s.id for s in tahoe.find(span.quote)] == [span.id]


def test_a_fabricated_quote_is_not_found(tahoe: spans.Document) -> None:
    """The test that matters: an invented requirement must not resolve to any span."""
    assert tahoe.locate("a dedicated 24x7 on-site team of eight engineers") == []
    assert tahoe.locate("") == []


def test_hyphenated_line_breaks_are_counted_not_repaired(tahoe: spans.Document) -> None:
    """The one artefact the module refuses to guess about, so it must at least be measured."""
    assert tahoe.hyphen_breaks >= 0
    assert isinstance(tahoe.hyphen_breaks, int)


@pytest.mark.parametrize("name", sorted(cli.manifest_hashes()))
def test_every_provenanced_fixture_parses_and_matches_its_published_hash(name: str) -> None:
    """All eleven fixtures build, and each one is the document the manifest says it is."""
    doc = spans.build(cli.FIXTURES / name, fixture_name=name)
    assert doc.fixture_sha256 == cli.manifest_hashes()[name]
    assert doc.pages, "no pages extracted"
    assert len(doc.spans) > 20, f"implausibly few spans: {len(doc.spans)}"


def test_index_round_trip(tmp_path) -> None:
    doc = spans.build(cli.FIXTURES / TAHOE, fixture_name=TAHOE)
    out = spans.write_index(doc, tmp_path / "index.json")
    data = spans.read_index(out)
    assert data["schema"] == "span-index/1"
    assert data["span_count"] == len(doc.spans)
    assert spans.reproducibility_report(doc, data) == []


def test_reproducibility_report_catches_a_changed_engine(tahoe: spans.Document) -> None:
    data = tahoe.to_json()
    data["engine_version"] = "pdftotext version 0.0.1 (imaginary)"
    problems = spans.reproducibility_report(tahoe, data)
    assert any("engine changed" in p for p in problems)


def test_reproducibility_report_catches_a_changed_page(tahoe: spans.Document) -> None:
    data = tahoe.to_json()
    data["pages"][3]["sha256"] = "0" * 64
    problems = spans.reproducibility_report(tahoe, data)
    assert any("page text differs" in p for p in problems)


def test_build_refuses_a_fixture_with_no_provenance_row(tmp_path, capsys) -> None:
    """The gate that ties parsing to provenance: an unlisted document cannot be indexed."""
    stray = tmp_path / "unlisted-document.pdf"
    stray.write_bytes((cli.FIXTURES / TAHOE).read_bytes())
    rc = cli.main(["build", str(stray), "--out", str(tmp_path / "x.json")])
    assert rc == 2
    assert "no provenance row" in capsys.readouterr().err
    assert not (tmp_path / "x.json").exists()


def test_cli_verify_fails_a_stale_index(tmp_path, capsys) -> None:
    doc = spans.build(cli.FIXTURES / TAHOE, fixture_name=TAHOE)
    out = spans.write_index(doc, tmp_path / "index.json")
    data = json.loads(out.read_text())
    data["fixture_sha256"] = "f" * 64
    out.write_text(json.dumps(data))
    rc = cli.main(["verify", str(out)])
    assert rc == 1
    assert "NOT reproducible" in capsys.readouterr().err


def test_word_boundaries_are_required(tahoe: spans.Document) -> None:
    """A quote may start mid-span but never mid-word. Truncation is not a citation."""
    assert tahoe.locate("be on-site within four (4) hour") == [], "truncated word must not match"
    assert tahoe.locate("on-site within four"), "a whole-word run inside a span is fine"


def test_cli_find_separates_a_substring_from_a_span(tahoe, capsys) -> None:
    """Containment by default; `--exact` is the stricter question, and a substring fails it."""
    inside = " ".join(tahoe.spans[5].quote.split()[:5])
    assert inside and inside != tahoe.spans[5].quote, "the sample must be a proper substring"

    assert cli.main(["find", str(cli.FIXTURES / TAHOE), inside]) == 0
    assert tahoe.spans[5].id in capsys.readouterr().out

    assert cli.main(["find", str(cli.FIXTURES / TAHOE), inside, "--exact"]) == 1
    assert "no span equals that quote" in capsys.readouterr().err


def test_cli_find_exits_nonzero_on_an_ambiguous_quote(tahoe, capsys) -> None:
    """A quote on several pages is not yet a citation; the CLI refuses to pick one for you."""
    short = tahoe.spans[5].quote.split()[0]
    rc = cli.main(["find", str(cli.FIXTURES / TAHOE), short])
    if len(tahoe.locate(short)) > 1:
        assert rc == 1
        assert "ambiguous" in capsys.readouterr().err
