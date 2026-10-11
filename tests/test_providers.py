"""Provider probe tests. Offline: the fetcher is injected, so no network is needed."""

from __future__ import annotations

import json

from rfpbrief import providers

NOT_FOUND = (404, '{"error":{"message":"Not Found","code":404}}')
CATALOGUE_WITHOUT_IT = (200, json.dumps({"data": [{"id": "openai/gpt-5"}, {"id": "anthropic/claude-4"}]}))
MODEL_CARD = (200, json.dumps({"data": {"id": providers.WANTED, "name": "Microsoft: Microsoft-Decision-1",
                                        "context_length": 32768}}))


def _fetch(catalogue=CATALOGUE_WITHOUT_IT, model=NOT_FOUND):
    def fetch(url: str) -> tuple[int, str]:
        return catalogue if url.endswith("/models") else model
    return fetch


def _call(ok: bool = True):
    def call(model: str, prompt: str) -> tuple[int, str]:
        if not ok:
            return 402, '{"error":{"message":"Insufficient credits"}}'
        return 200, json.dumps({"choices": [{"message": {"content": '{"ok": true}'}}]})
    return call


def _decisions_call():
    """Simulates the real 2026-10-11 behaviour: chat refuses, the decisions endpoint answers."""
    seen = []

    def call(model: str, prompt: str) -> tuple[int, str]:
        seen.append("chat")
        return 200, json.dumps({
            "model": f"{model}-20261009",
            "answers": {"ok": {"type": "noul", "noul": 0.0086}},
            "usage": {"input_tokens": 193, "output_tokens": 1, "cost": 8.1e-06},
        })
    call.seen = seen
    return call


def test_a_404_metadata_endpoint_does_not_decide_callability() -> None:
    """The mistake this module shipped with: it called a 404 on `/models/<id>` "not callable".

    That is what it reported for `typesafe/jev-router` on 2026-10-11 while inference worked fine.
    Callability is now decided by making a call; the metadata signals are informational.
    """
    p = providers.probe(fetch=_fetch(), call=_call())
    assert p.model_status == 404, "the metadata endpoint still says 404"
    assert p.in_catalogue is False
    assert p.callable_now is True, "but the model answers, so it is callable"
    rendered = providers.render(p)
    assert "actual call    HTTP 200" in rendered
    assert "informational" in rendered
    assert "decided by making a call" in rendered


def test_a_served_model_shows_its_card_and_what_it_answered() -> None:
    p = providers.probe(fetch=_fetch(model=MODEL_CARD), call=_call())
    assert p.callable_now is True
    rendered = providers.render(p)
    assert "Microsoft-Decision-1" in rendered
    assert "32768" in rendered
    assert '{"ok": true}' in rendered, "the answer is evidence, not a boolean"


def test_a_model_served_before_the_catalogue_lists_it_is_still_callable() -> None:
    """Listings lag APIs as well as leading them, so the two signals stay separate."""
    p = providers.probe(fetch=_fetch(model=MODEL_CARD), call=_call())
    assert p.in_catalogue is False
    assert p.callable_now is True


def test_a_call_that_fails_reports_the_providers_error() -> None:
    p = providers.probe(fetch=_fetch(model=MODEL_CARD), call=_call(ok=False))
    assert p.callable_now is False
    assert "Insufficient credits" in providers.render(p)


def test_an_unreachable_provider_does_not_crash_the_probe() -> None:
    p = providers.probe(fetch=_fetch(catalogue=(0, "URLError: offline"), model=(0, "offline")),
                        call=_call())
    assert p.callable_now is True, "an offline catalogue does not make a working model uncallable"
    assert "catalogue unavailable" in p.note


def test_an_unreadable_catalogue_is_noted_rather_than_raised() -> None:
    p = providers.probe(fetch=_fetch(catalogue=(200, "not json")), call=_call(ok=False))
    assert "unreadable" in p.note
    assert p.callable_now is False


def test_a_decisions_model_is_callable_and_its_probability_is_the_evidence() -> None:
    """The correction this probe needed: a decisions model answers, on its own surface.

    `providers._call` retries the decisions endpoint when chat/completions refuses with
    "is a decisions model". Here the injected call stands in for that second request, so what is
    asserted is the reporting: the surface, the probability, and the resolved model version.
    """
    p = providers.probe(fetch=_fetch(), call=_decisions_call())
    assert p.callable_now is True
    assert p.surface == "decisions"
    rendered = providers.render(p)
    assert "on decisions" in rendered
    assert "noul" in rendered and "0.0086" in rendered
    assert "microsoft-decision-1-20261009" in rendered, "the resolved version is pinned in the record"


def test_a_chat_model_reports_the_chat_surface() -> None:
    p = providers.probe(fetch=_fetch(model=MODEL_CARD), call=_call())
    assert p.surface == "chat/completions"
    assert '{"ok": true}' in providers.render(p)
