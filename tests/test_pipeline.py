"""End-to-end slice tests: extraction → decision → brief, on the Tahoe fixture.

Offline and model-free. The point of this file is that the pipeline's central claim — every claim in
a brief traces to a span — is enforced here rather than asserted in a README.
"""

from __future__ import annotations

import copy
import json
import re
from pathlib import Path

import pytest

from rfpbrief import brief as brief_mod
from rfpbrief import decide as decide_mod
from rfpbrief import extract as extract_mod
from rfpbrief import parse as cli
from rfpbrief import spans

REPO = Path(__file__).resolve().parents[1]
TAHOE = "tahoe-transportation-district-it-consulting-2025.pdf"
TAHOE_PATH = cli.FIXTURES / TAHOE
EXTRACTION = REPO / "extractions" / f"{Path(TAHOE).stem}.json"
PROFILE = json.loads((REPO / "bidder-profile.json").read_text(encoding="utf-8"))
LABELS = json.loads((REPO / "fixtures" / "labels.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def doc() -> spans.Document:
    return spans.build(TAHOE_PATH, fixture_name=TAHOE)


@pytest.fixture(scope="module")
def extraction(doc) -> extract_mod.Extraction:
    return extract_mod.for_fixture(doc)


@pytest.fixture(scope="module")
def decision(extraction) -> decide_mod.Decision:
    return decide_mod.decide(PROFILE, extraction)


def _variant(tmp_path: Path, mutate) -> Path:
    data = copy.deepcopy(json.loads(EXTRACTION.read_text()))
    mutate(data)
    out = tmp_path / "variant.json"
    out.write_text(json.dumps(data), encoding="utf-8")
    return out


# ── extraction: the contract ──────────────────────────────────────────────────────────────────

def test_the_committed_extraction_validates(extraction) -> None:
    cites = extraction.citations()
    assert len(cites) == 12
    assert all(c.span_id and c.page and c.quote for c in cites)


def test_a_fabricated_quote_refuses_to_load(doc, tmp_path) -> None:
    """The test the whole design exists for: an invented quotation cannot enter the pipeline."""
    def mutate(data):
        data["facts"]["issuer"]["citations"][0]["quote"] = "County of Placer"

    with pytest.raises(extract_mod.ExtractionError) as exc:
        extract_mod.load(_variant(tmp_path, mutate), doc)
    assert any("verbatim rule" in p for p in exc.value.problems)


def test_a_wrong_span_id_refuses_to_load(doc, tmp_path) -> None:
    def mutate(data):
        data["facts"]["issuer"]["citations"][0]["span_id"] = "p9-s99"

    with pytest.raises(extract_mod.ExtractionError) as exc:
        extract_mod.load(_variant(tmp_path, mutate), doc)
    assert any("does not exist" in p for p in exc.value.problems)


def test_a_wrong_page_refuses_to_load(doc, tmp_path) -> None:
    def mutate(data):
        data["facts"]["issuer"]["citations"][0]["page"] = 40

    with pytest.raises(extract_mod.ExtractionError) as exc:
        extract_mod.load(_variant(tmp_path, mutate), doc)
    assert any("citation says page" in p for p in exc.value.problems)


def test_an_uncited_field_refuses_to_load(doc, tmp_path) -> None:
    def mutate(data):
        data["facts"]["term"]["citations"] = []

    with pytest.raises(extract_mod.ExtractionError) as exc:
        extract_mod.load(_variant(tmp_path, mutate), doc)
    assert any("no citation" in p for p in exc.value.problems)


def test_all_problems_are_reported_not_just_the_first(doc, tmp_path) -> None:
    def mutate(data):
        data["facts"]["issuer"]["citations"][0]["span_id"] = "nope"
        data["facts"]["term"]["citations"] = []
        data["facts"]["subject"]["citations"][0]["quote"] = "invented"

    with pytest.raises(extract_mod.ExtractionError) as exc:
        extract_mod.load(_variant(tmp_path, mutate), doc)
    assert len(exc.value.problems) >= 3


# ── decision: the profile is the source of truth ──────────────────────────────────────────────

def test_decision_is_no_bid_in_geography(decision) -> None:
    assert decision.recommendation == decide_mod.NO_BID
    assert decision.primary_reason_class == "geography"
    assert len(decision.reasons) == 3


def test_decision_matches_the_committed_ground_truth(decision) -> None:
    """n = 1, and it is labelled n = 1 rather than called an evaluation."""
    label = next(g for g in LABELS["labels"] if g["fixture"] == TAHOE)
    assert decision.recommendation == label["label"]
    assert decision.primary_reason_class == label["reason_class"]


def test_every_reason_cites_both_the_fixture_and_the_profile(decision) -> None:
    for reason in decision.reasons:
        assert reason.citations, reason.requirement
        assert reason.profile_exclusion in " ".join(decide_mod.profile_exclusions(PROFILE))


def test_every_binding_phrase_is_present_in_the_frozen_profile() -> None:
    """The profile stays the source of truth; a binding may not invent an exclusion."""
    for binding in decide_mod.BINDINGS:
        assert decide_mod.profile_carries(PROFILE, binding.profile_exclusion), binding


def test_removing_the_exclusions_flips_the_call(extraction) -> None:
    """'Edit one line of the profile and watch the call move' — demonstrated, not claimed."""
    variant = copy.deepcopy(PROFILE)
    variant["excluded_delivery_models"] = [
        e for e in variant["excluded_delivery_models"]
        if "regular on-site staffing" not in e and "24×7 monitoring" not in e
    ]
    flipped = decide_mod.decide(variant, extraction)
    assert flipped.recommendation == decide_mod.BID
    assert flipped.primary_reason_class == "in_scope"


def test_the_probability_is_not_fabricated(decision) -> None:
    assert decision.probability is None
    assert any("no calibrated probability" in n for n in decision.notes)


# ── brief: the artifact ───────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def rendered(decision, extraction, doc) -> str:
    return brief_mod.render(decision, extraction, doc)


def test_brief_states_the_recommendation_and_the_class(rendered) -> None:
    assert "recommendation: **NO-BID**" in rendered
    assert "Primary reason class: **Geography**" in rendered


def test_brief_is_deterministic(decision, extraction, doc, rendered) -> None:
    assert brief_mod.render(decision, extraction, doc) == rendered


_CITE_RE = re.compile(r'"([^"]*)" \(page (\d+), span `([^`]+)`\)')


def spans_of(markdown: str) -> list[tuple[str, str]]:
    """Every (span_id, quote) pair the brief claims. Used to re-verify the artifact itself."""
    return [(m.group(3), m.group(1)) for m in _CITE_RE.finditer(markdown)]


def test_the_brief_carries_every_requirement_quote(rendered) -> None:
    quotes = {q for _, q in spans_of(rendered)}
    for expected in (
        "be on-site within four (4) hours",
        "two (2) days per week",
        "20 hours of IT support",
    ):
        assert any(expected in q for q in quotes), expected


def test_every_quote_in_the_rendered_brief_re_verifies(rendered, doc) -> None:
    """Read the artifact back and check it against the fixture: a brief is evidence, so re-verify it."""
    pairs = spans_of(rendered)
    assert len(pairs) >= 6, "the brief should carry every citation it makes"
    for span_id, quote in pairs:
        assert doc.validate_citation(span_id, quote), (span_id, quote)


def test_an_invented_quote_in_the_brief_would_fail_the_re_check(rendered, doc) -> None:
    """Negative control: the re-check above has teeth, or it proves nothing."""
    doctored = rendered.replace("be on-site within four (4) hours", "be on-site within two (2) hours")
    bad = [p for p in spans_of(doctored) if not doc.validate_citation(*p)]
    assert bad, "the doctored brief must produce at least one failing citation"


# ── the artifacts a fixture produces ──────────────────────────────────────────────────────────

def test_brief_writes_a_file(tmp_path) -> None:
    rc = cli.main(["brief", str(TAHOE_PATH), "--out", str(tmp_path / "b.md"), "--quiet"])
    assert rc == 0
    assert "NO-BID" in (tmp_path / "b.md").read_text()


def test_a_fixture_without_an_extraction_says_so(tmp_path) -> None:
    """Every fixture has one today, so the check is against an empty extraction directory — and
    the message says which fixture cannot be briefed rather than failing obscurely."""
    other = cli.FIXTURES / "city-of-spicer-mn-managed-it-services-2026.pdf"
    d = spans.build(other, fixture_name=other.name)
    with pytest.raises(FileNotFoundError) as exc:
        extract_mod.for_fixture(d, tmp_path)
    assert "cannot be briefed" in str(exc.value)


# ── the rule-based baseline over the whole labelled set ───────────────────────────────────────

def _baseline():
    from rfpbrief import evaluate
    def extraction_for(fixture: str):
        path = cli.FIXTURES / fixture
        if not path.exists():
            return None
        d = spans.build(path, fixture_name=fixture)
        try:
            return extract_mod.for_fixture(d)
        except FileNotFoundError:
            return None
    return evaluate.run(LABELS, extraction_for, lambda ex: decide_mod.decide(PROFILE, ex))


def test_every_labelled_fixture_has_an_extraction_and_agrees_on_the_label() -> None:
    """11/11 on the call. This checks the decision layer and the vocabulary, not extraction:
    the extractions were hand-authored knowing the labels, and baseline.json says so."""
    base = _baseline()
    assert base.missing_extraction == []
    assert base.n == len(LABELS["labels"]) == 11
    assert base.label_agree == base.n
    assert base.confusion() == {"bid": {"bid": 4}, "no_bid": {"no_bid": 7}}


def test_the_labelled_reason_class_is_always_found() -> None:
    """The layer may rank reasons differently; it may not miss the reason the label names."""
    base = _baseline()
    assert base.class_found == base.n


def test_the_one_ranking_divergence_is_known_and_named() -> None:
    """Two fixtures trigger geography AND operations, and their labels rank them in opposite
    directions — so no single priority order reproduces both. Pinned so a change in PRIORITY is
    visible rather than silent."""
    base = _baseline()
    assert base.ranking_divergences == [
        "palm-beach-mpo-rfp-2026-07-it-services.pdf"
    ]
    assert base.class_agree == base.n - 1
