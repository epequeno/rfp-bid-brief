"""Tests for the variance measurement. Offline: they build run directories and classify them."""

from __future__ import annotations

import json

from rfpbrief import variance


def _run(tmp_path, name, clean=(), repaired=(), refused=()):
    d = tmp_path / name
    d.mkdir()
    for fixture in clean:
        (d / f"{fixture}.json").write_text(json.dumps({"fixture": fixture, "extractor": {"attempts": 1}}))
    for fixture in repaired:
        (d / f"{fixture}.json").write_text(json.dumps({"fixture": fixture, "extractor": {"attempts": 2}}))
    if refused:
        (d / "_refused").mkdir()
        for fixture in refused:
            (d / "_refused" / f"{fixture}.json").write_text(json.dumps({"fixture": fixture}))
    return d


def test_three_outcomes_are_kept_apart(tmp_path) -> None:
    """Repaired is not clean. Collapsing them would hide the thing being measured."""
    run = variance.read_run(_run(tmp_path, "run-1", clean=["a"], repaired=["b"], refused=["c"]))
    assert (run.clean, run.repaired, run.refused) == (["a"], ["b"], ["c"])
    assert run.total == 3
    assert run.outcome_for("a") == variance.CLEAN
    assert run.outcome_for("b") == variance.REPAIRED
    assert run.outcome_for("c") == variance.REFUSED


def test_the_spread_is_reported_not_averaged(tmp_path) -> None:
    r1 = variance.read_run(_run(tmp_path, "run-1", clean=["a"], repaired=["b"]))
    r2 = variance.read_run(_run(tmp_path, "run-2", clean=["a", "b"]))
    v = variance.summarise([r1, r2])
    assert v.clean_range == (1, 2)
    assert v.stability("a") == variance.CLEAN
    assert v.stability("b") == "varies"


def test_a_fixture_clean_every_run_is_distinguishable_from_one_that_varies(tmp_path) -> None:
    r1 = variance.read_run(_run(tmp_path, "run-1", clean=["a"], repaired=["b"]))
    r2 = variance.read_run(_run(tmp_path, "run-2", clean=["a"], repaired=["b"]))
    v = variance.summarise([r1, r2])
    assert v.stability("a") == variance.CLEAN and v.stability("b") == variance.REPAIRED
    assert v.to_json()["stability_counts"] == {"clean": 1, "repaired": 1, "refused": 0, "varies": 0}


def test_usable_after_repair_is_reported_separately_from_clean(tmp_path) -> None:
    r1 = variance.read_run(_run(tmp_path, "run-1", clean=["a"], repaired=["b"], refused=["c"]))
    payload = variance.summarise([r1]).to_json()
    assert payload["clean_first_attempt"]["per_run"] == [1]
    assert payload["clean_first_attempt"]["usable_after_repair"] == [2]


def test_the_payload_says_what_it_measures(tmp_path) -> None:
    v = variance.summarise([variance.read_run(_run(tmp_path, "run-1", clean=["a"]))])
    payload = v.to_json()
    assert "not a rate" in payload["what_this_measures"]
    assert "varies" in payload["note"]
