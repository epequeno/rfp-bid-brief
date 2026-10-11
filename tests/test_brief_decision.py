"""The brief must not contradict the census, and must not invent a number when there is none.

Written because it did contradict it: eleven committed briefs said "no calibrated probability is
available yet" while `results/calibration.json` sat beside them with fourteen models' probabilities.
A stale claim in a rendered artifact is not a typo; it is the artifact lying about its own contents.
"""

import json
from pathlib import Path

from rfpbrief import brief, calibrate
from rfpbrief.decide import Decision

REPO = Path(__file__).resolve().parents[1]
SPLIT = "energy-trust-of-oregon-crm-migration-to-d365.pdf"
UMAINE = "u-maine-system-rfp-2026-065-enterprise-genai-services.pdf"


def _decisions() -> dict:
    return json.loads((REPO / "results" / "decisions.json").read_text(encoding="utf-8"))


def _calibration() -> dict:
    return json.loads((REPO / "results" / "calibration.json").read_text(encoding="utf-8"))


def _decision(recommendation: str = "no_bid") -> Decision:
    return Decision(recommendation=recommendation, probability=None, primary_reason_class="in_scope",
                    reasons=[], considered=[], notes=[])


def test_the_stale_claim_cannot_come_back_unnoticed():
    src = (REPO / "src" / "rfpbrief" / "decide.py").read_text(encoding="utf-8")
    assert "no calibrated probability is available" not in src


def test_no_census_means_no_number_is_shown():
    text = "\n".join(brief._decision_section(_decision(), None))
    assert "no probability is shown" in text
    assert "P(bid)" not in text


def test_the_real_census_is_reported_for_a_unanimous_fixture():
    verdict = calibrate.fixture_verdict(_decisions(), _calibration(), UMAINE)
    text = "\n".join(brief._decision_section(_decision(), verdict))
    assert verdict.bid == 0 and verdict.no_bid == 14 and not verdict.contested
    assert "P(bid)" in text and "τ = 0.50" in text
    assert "Census of 14 served decision models" in text
    assert "Every model in the census read this solicitation the same way." in text
    assert "same** call as the channel" in text


def test_the_committed_split_fixture_is_reported_as_contested():
    verdict = calibrate.fixture_verdict(_decisions(), _calibration(), SPLIT)
    assert verdict.contested and (verdict.bid, verdict.no_bid) == (7, 7)
    text = "\n".join(brief._decision_section(_decision(), verdict))
    assert "disagree with each other" in text


def test_the_resolved_build_and_provider_travel_with_the_probability():
    verdict = calibrate.fixture_verdict(_decisions(), _calibration(), UMAINE)
    assert verdict.channel["resolved"].startswith("typesafe/jev-1.13")
    assert verdict.channel["provider"] == "TypeSafe"
    assert verdict.comparator["resolved"].startswith("microsoft/microsoft-decision-1")
    assert verdict.comparator["provider"] == "Azure"


def test_a_disagreement_between_the_rules_layer_and_the_channel_is_not_averaged_away():
    verdict = calibrate.fixture_verdict(_decisions(), _calibration(), UMAINE)
    pulled_the_other_way = _decision("bid")  # the channel says no-bid; the rules layer says bid
    text = "\n".join(brief._decision_section(pulled_the_other_way, verdict))
    assert "**disagrees** with the channel" in text


def test_every_committed_fixture_has_a_full_census_behind_it():
    d, c = _decisions(), _calibration()
    fixtures = sorted({a["fixture"] for a in d["answers"]})
    assert len(fixtures) == 11
    for f in fixtures:
        v = calibrate.fixture_verdict(d, c, f)
        assert v.total == 14, f
        assert v.lo is not None and v.hi is not None and v.lo <= v.hi, f


def test_the_reported_probability_is_the_one_recorded_for_that_fixture():
    """Regression: the channel lookup once matched on model slug alone, so a brief showed a
    probability belonging to a different solicitation. Counts were right, the number was not."""
    d = _decisions()
    recorded = {(a["fixture"], a["model_requested"]): a["noul"] for a in d["answers"]}
    fixtures = sorted({a["fixture"] for a in d["answers"]})
    for f in fixtures:
        v = calibrate.fixture_verdict(d, _calibration(), f)
        assert v.channel["probability"] == recorded[(f, "typesafe/jev-1.13")], f
        assert v.comparator["probability"] == recorded[(f, "microsoft/microsoft-decision-1")], f
        assert v.lo <= v.channel["probability"] <= v.hi, f
