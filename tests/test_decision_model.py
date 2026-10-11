"""Tests for the decision census. Offline: every call is injected, so no test spends money."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from rfpbrief import decide, decision_model, extract, spans
from rfpbrief import parse as cli

REPO = Path(__file__).resolve().parents[1]
TAHOE = "tahoe-transportation-district-it-consulting-2025.pdf"
PROFILE = json.loads((REPO / "bidder-profile.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def tahoe() -> tuple[spans.Document, extract.Extraction]:
    doc = spans.build(cli.FIXTURES / TAHOE, fixture_name=TAHOE)
    return doc, extract.for_fixture(doc)


# ── the state: identical for every model, and complete about the profile ───────────────────────

def test_the_state_is_deterministic(tahoe) -> None:
    doc, ex = tahoe
    assert decision_model.build_state(PROFILE, ex) == decision_model.build_state(PROFILE, ex)


def test_the_state_carries_every_phrase_the_rules_layer_cites(tahoe) -> None:
    """The two judges must be given the same profile, or a disagreement means nothing.

    This is the test that would have caught a real bug: `build_state` once omitted the profile's
    rules of thumb, and the phrase the deterministic layer cites for the D365 case lives only there.
    Every model then read the exclusions literally and unanimously said `bid` where the label says
    `no_bid` — which looked like fourteen models disagreeing with a label and was in fact one
    incomplete state.
    """
    doc, ex = tahoe
    state = decision_model.build_state(PROFILE, ex)
    cited = [b.profile_exclusion for b in decide.BINDINGS
             if decide.profile_carries(PROFILE, b.profile_exclusion)]
    assert cited, "the fixture set should exercise at least one binding"
    for phrase in cited:
        assert phrase in state, f"the state omits a phrase the rules layer relies on: {phrase!r}"


def test_the_state_carries_the_evidence_not_just_the_values(tahoe) -> None:
    doc, ex = tahoe
    state = decision_model.build_state(PROFILE, ex)
    assert 'the fixture says' not in state  # that is brief phrasing, not state
    for fact in ex.requirements.values():
        for c in fact.citations:
            assert c.quote in state, "a model cannot weigh evidence it was not shown"


def test_the_request_is_identical_for_every_model(tahoe) -> None:
    """Only the model field may differ, or the comparison measures phrasing rather than models."""
    doc, ex = tahoe
    state = decision_model.build_state(PROFILE, ex)
    a = decision_model.request_body("typesafe/jev-1.13", state)
    b = decision_model.request_body("microsoft/microsoft-decision-1", state)
    assert a["state"] == b["state"] and a["questions"] == b["questions"]
    assert {k: v for k, v in a.items() if k != "model"} == {k: v for k, v in b.items() if k != "model"}


def test_the_frozen_request_hash_is_stable() -> None:
    assert decision_model.frozen_request_sha256() == decision_model.frozen_request_sha256()
    assert len(decision_model.frozen_request_sha256()) == 64


# ── the census: filtered by rule, not by taste ────────────────────────────────

CENSUS_BODY = json.dumps({"data": [
    {"id": "vendor/decide-1.2", "canonical_slug": "vendor/decide-1.2-20260101",
     "context_length": 65536, "pricing": {"prompt": "0.00004"}, "created": 1},
    {"id": "~vendor/decide-latest", "canonical_slug": "~vendor/decide-latest",
     "context_length": 65536, "pricing": {"prompt": "0.00004"}, "created": 1},
    {"id": "vendor/decide-1.2:free", "canonical_slug": "vendor/decide-1.2-20260101",
     "context_length": 65536, "pricing": {"prompt": "0"}, "created": 1},
    {"id": "other/behaviours", "canonical_slug": "other/behaviours-20260101",
     "context_length": 0, "pricing": {"prompt": "0.00002"}, "created": 1},
]})


def _fetch(body: str = CENSUS_BODY):
    def fetch(url: str) -> tuple[int, str]:
        return 200, body
    return fetch


def test_aliases_free_tiers_and_contextless_entries_are_excluded_by_rule() -> None:
    candidates, taken = decision_model.census(fetch=_fetch())
    assert taken and len(taken) == 10
    by_canonical = {c.canonical: c for c in candidates}
    assert by_canonical["vendor/decide-1.2-20260101"].eligible
    assert "alias" in by_canonical["vendor/decide-latest"].excluded_because
    assert "no declared context" in by_canonical["other/behaviours-20260101"].excluded_because
    assert sum(c.eligible for c in candidates) == 1, "the free tier must not double-count"


def test_an_unavailable_census_raises_rather_than_shrinking_silently() -> None:
    def fetch(url: str) -> tuple[int, str]:
        return 503, "upstream down"
    with pytest.raises(RuntimeError) as exc:
        decision_model.census(fetch=fetch)
    assert "census unavailable" in str(exc.value)


# ── asking: record what answered ──────────────────────────────────────────────

def test_an_answer_records_the_version_and_host() -> None:
    def post(url: str, body: dict) -> tuple[int, str]:
        return 200, json.dumps({"model": "vendor/decide-1.2-20260101", "provider": "Azure",
                                "answers": {"bid": {"type": "noul", "noul": 0.25}},
                                "usage": {"input_tokens": 400, "output_tokens": 1, "cost": 1.6e-05}})
    a = decision_model.ask("vendor/decide-1.2", "state", post=post)
    assert a.ok and a.noul == 0.25
    assert a.resolved == "vendor/decide-1.2-20260101" and a.provider == "Azure" and a.cost


def test_a_refusal_is_recorded_not_raised() -> None:
    def post(url: str, body: dict) -> tuple[int, str]:
        return 400, json.dumps({"error": {"message": "noul is not supported"}})
    a = decision_model.ask("vendor/model", "state", post=post)
    assert not a.ok and "not supported" in a.error


def test_an_unreadable_answer_is_a_refusal() -> None:
    def post(url: str, body: dict) -> tuple[int, str]:
        return 200, '{"answers": {}}'
    a = decision_model.ask("vendor/model", "state", post=post)
    assert not a.ok and "unreadable" in a.error


def test_the_run_asks_every_eligible_model_once_per_fixture(tahoe) -> None:
    doc, ex = tahoe
    candidates, taken = decision_model.census(fetch=_fetch())
    seen: list[tuple[str, str]] = []

    def fake_ask(model: str, state: str) -> decision_model.Answer:
        seen.append((model, state))
        return decision_model.Answer(model=model, status=200, noul=0.4, resolved=model + "-x",
                                     provider="Test", cost=1e-05)

    result = decision_model.run([(doc, ex)], PROFILE, candidates, 0.5, taken, ask_fn=fake_ask)
    assert len(seen) == 1, "aliases and contextless entries must not be asked"
    assert all(state == seen[0][1] for _, state in seen), "one state, byte-identical"
    payload = result.to_json()
    assert payload["answers"][0]["model_canonical"] == seen[0][0]
    assert payload["operating_point_tau"] == 0.5
    assert "same state and the same questions" in payload["note"]
