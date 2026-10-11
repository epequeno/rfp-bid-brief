"""Tests for the repair channel (ADR 0006).

The model is injected, so the whole retry loop is exercised offline: no network, no API key, no
nondeterminism. What is asserted is not that a model behaves well — it is that the loop is bounded,
that the repair is targeted, and that a refusal still refuses.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from rfpbrief import extract as extract_mod
from rfpbrief import model_extractor
from rfpbrief import parse as cli
from rfpbrief import spans

REPO = Path(__file__).resolve().parents[1]
TAHOE = "tahoe-transportation-district-it-consulting-2025.pdf"
GOOD = json.loads((REPO / "extractions" / f"{Path(TAHOE).stem}.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def doc() -> spans.Document:
    return spans.build(cli.FIXTURES / TAHOE, fixture_name=TAHOE)


def _broken() -> dict:
    """The good extraction with one citation's quote altered — a capitalisation change."""
    data = copy.deepcopy(GOOD)
    data["facts"]["issuer"]["citations"][0]["quote"] = "TAHOE TRANSPORTATION DISTRICT"
    return data


def _scripted(responses: list[str]):
    """A caller that returns queued responses and records the prompts it was given."""
    seen: list[str] = []

    def caller(prompt: str, model: str) -> str:
        seen.append(prompt)
        return responses[min(len(seen) - 1, len(responses) - 1)]

    caller.seen = seen  # type: ignore[attr-defined]
    return caller


def test_a_good_first_answer_needs_no_repair(doc) -> None:
    caller = _scripted([json.dumps(GOOD)])
    run = model_extractor.extract(doc, caller=caller)
    assert run.accepted and run.attempts == 1
    assert not run.repaired
    assert len(caller.seen) == 1


def test_a_refusal_is_fed_back_and_a_fixed_answer_is_accepted(doc) -> None:
    """The behaviour ADR 0006 exists for: the diagnosis reaches the producer."""
    caller = _scripted([json.dumps(_broken()), json.dumps(GOOD)])
    run = model_extractor.extract(doc, caller=caller)
    assert run.accepted and run.attempts == 2 and run.repaired
    assert len(caller.seen) == 2
    repair_prompt = caller.seen[1]
    assert "refused by the citation gate" in repair_prompt
    assert "TAHOE TRANSPORTATION DISTRICT" in repair_prompt, "the offending quote is named"
    assert "everything else unchanged" in repair_prompt, "the retry must not re-roll the values"


def test_the_loop_is_bounded(doc) -> None:
    """Two attempts happen; a third does not. An unbounded retry is a search, not a measurement."""
    caller = _scripted([json.dumps(_broken())])
    run = model_extractor.extract(doc, caller=caller, retries=1)
    assert not run.accepted
    assert run.attempts == 2
    assert len(caller.seen) == 2
    assert len(run.refusals) == 2
    assert run.first_attempt_problems, "the first refusal is kept, not overwritten"


def test_retries_zero_means_one_attempt(doc) -> None:
    caller = _scripted([json.dumps(_broken())])
    run = model_extractor.extract(doc, caller=caller, retries=0)
    assert run.attempts == 1 and not run.accepted and len(caller.seen) == 1


def test_a_non_json_response_is_a_refusal_not_a_crash(doc) -> None:
    caller = _scripted(["I'm sorry, I can't help with that."])
    run = model_extractor.extract(doc, caller=caller, retries=0)
    assert not run.accepted
    assert "not JSON" in run.refusals[0]["problems"][0]


def test_a_fenced_json_response_is_accepted(doc) -> None:
    caller = _scripted(["```json\n" + json.dumps(GOOD) + "\n```"])
    run = model_extractor.extract(doc, caller=caller)
    assert run.accepted


def test_a_model_error_is_recorded_rather_than_raised(doc) -> None:
    def boom(prompt: str, model: str) -> str:
        raise RuntimeError("upstream 502")

    run = model_extractor.extract(doc, caller=boom)
    assert not run.accepted
    assert run.error and "502" in run.error


def test_the_prompt_and_payload_are_what_the_extractor_sees(doc) -> None:
    payload = model_extractor.payload_for(doc)
    assert payload.startswith(f"fixture: {TAHOE}")
    assert "[p1-s0] (page 1)" in payload
    # No expectations of any kind travel with the spans: not the label, not the schema keys, not the
    # profile. "requirements" as an English word does appear inside span text, so check the keys.
    for leak in ('"facts"', '"citations"', '"value"', "requires_recurring_onsite",
                 "functional_stacks", "no_bid", "bidder-profile"):
        assert leak not in payload, leak


def test_annotation_records_how_hard_it_was(doc) -> None:
    caller = _scripted([json.dumps(_broken()), json.dumps(GOOD)])
    run = model_extractor.extract(doc, caller=caller)
    data = model_extractor.annotate(run, run.data, "start", "finish")
    ext = data["extractor"]
    assert ext["attempts"] == 2
    assert ext["repaired_after_refusal"] is True
    assert ext["refusals"][0]["problems"]
    assert len(ext["prompt_sha256"]) == 64
    assert "no label" in ext["inputs"]


def test_a_refused_run_is_written_outside_the_extraction_directory(doc, tmp_path, capsys) -> None:
    """A refused extraction must never sit where a comparison would read it as data."""
    caller = _scripted([json.dumps(_broken())])
    model_extractor.call_pi = caller  # type: ignore[assignment]
    rc = cli.main(["model-extract", str(cli.FIXTURES / TAHOE), "--out-dir", str(tmp_path)])
    assert rc == 1
    assert not list(tmp_path.glob("*.json")), "nothing may land in the extraction directory"
    refused = list((tmp_path / "_refused").glob("*.json"))
    assert refused and "refusals" in refused[0].read_text()
    assert "REFUSED" in capsys.readouterr().err


def test_the_diagnosis_names_the_differing_character() -> None:
    """A refusal must say what to change, not only that something is wrong.

    The model wrote an ASCII apostrophe where the document has U+2019. That is the one failure mode
    a producer can fix if — and only if — it is told which character differs, so the diagnosis is
    asserted here rather than trusted.
    """
    name = "inprs-rfp-23-04-cloud-migration-iam-ztna.pdf"
    doc = spans.build(cli.FIXTURES / name, fixture_name=name)
    payload = {
        "fixture": name,
        "facts": {"issuer": {"value": "x", "citations": [{
            "span_id": "p11-s0", "page": 11,
            "quote": "a thorough and complete assessment of INPRS's current systems"}]}},
        "requirements": {},
    }
    problems = extract_mod.validate(doc, payload)
    assert problems, "an ASCII apostrophe must not pass"
    assert "character" in problems[0]
    assert "\u2019" in problems[0], "the document's own character must appear in the diagnosis"
