"""The fifth exclusion class must be reachable from an extraction, not merely declared in the profile.

ADR 0012 added `not_qualified`; a class that exists in the profile and in labels.json but that no
binding can ever produce would be decoration. These tests are what make it a class rather than a note.
"""

import json
from pathlib import Path

from rfpbrief import decide
from rfpbrief.extract import Extraction, Fact

REPO = Path(__file__).resolve().parents[1]
PROFILE = json.loads((REPO / "bidder-profile.json").read_text(encoding="utf-8"))
LABELS = json.loads((REPO / "fixtures" / "labels.json").read_text(encoding="utf-8"))


def _fact(name, value):
    return Fact(name=name, value=value, citations=())


def _extraction(**requirements) -> Extraction:
    return Extraction(fixture="x.pdf", produced_by="test",
                      facts={}, requirements={k: _fact(k, v) for k, v in requirements.items()})


def test_an_eligibility_gate_makes_the_verdict_unreachable():
    d = decide.decide(PROFILE, _extraction(eligibility_gates=["comparable_implementations"]))
    assert d.recommendation == "no_bid"
    assert d.primary_reason_class == "not_qualified"
    assert "ineligible before capability" in d.reasons[0].summary


def test_unreachable_outranks_unsuitable():
    """A gated procurement that is ALSO a product purchase reports the gate as primary: the firm is
    not merely wrong for the work, it cannot bid on it."""
    d = decide.decide(PROFILE, _extraction(eligibility_gates=["comparable_implementations"], requires_product_supply=True))
    assert d.primary_reason_class == "not_qualified"
    assert {"not_qualified", "product_not_services"} <= {r.reason_class for r in d.reasons}


def test_no_fact_means_no_trigger():
    """Backward compatibility matters: eleven extractions were authored before this binding existed."""
    d = decide.decide(PROFILE, _extraction(requires_product_supply=False))
    assert d.recommendation == "bid"
    assert d.primary_reason_class == "in_scope"


def test_the_profile_labels_and_decide_agree_on_the_class_vocabulary():
    """The three places a class must exist, kept in sync by test rather than by memory."""
    declared = set(PROFILE["excluded_capability_areas"]) | set(PROFILE["excluded_delivery_models"]) | set(PROFILE["excluded_eligibility_gates"])
    assert PROFILE["excluded_eligibility_gates"]
    from_labels = set(LABELS["reason_classes"]) - {"in_scope"}
    from_decide = {b.reason_class for b in decide.BINDINGS}
    assert from_labels == from_decide == set(decide.PRIORITY), (from_labels, from_decide)
    assert declared  # the profile says it somewhere, in prose


def test_an_empty_gate_list_is_not_a_gate():
    d = decide.decide(PROFILE, _extraction(eligibility_gates=[]))
    assert d.recommendation == "bid"


def test_a_gate_shape_the_profile_does_not_exclude_is_only_a_consideration():
    """The profile, and only the profile, decides capability. An unrecognised gate shape must not
    silently become a no-bid."""
    d = decide.decide(PROFILE, _extraction(eligibility_gates=["something_else"]))
    assert d.recommendation == "bid"
