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


def test_a_listed_but_unserved_model_is_not_callable() -> None:
    """The situation on 2026-10-11: the announcement exists, the API answers 404."""
    p = providers.probe(fetch=_fetch())
    assert p.catalogue_status == 200
    assert p.in_catalogue is False
    assert p.model_status == 404
    assert p.callable_now is False
    assert "does not serve it yet" in providers.render(p)


def test_a_served_model_is_callable_and_its_card_is_shown() -> None:
    p = providers.probe(fetch=_fetch(model=MODEL_CARD))
    assert p.callable_now is True
    rendered = providers.render(p)
    assert "Microsoft-Decision-1" in rendered
    assert "32768" in rendered
    assert "does not serve it yet" not in rendered


def test_a_model_served_before_the_catalogue_lists_it_is_still_callable() -> None:
    """Listings lag APIs as well as leading them, so the two signals stay separate."""
    p = providers.probe(fetch=_fetch(model=MODEL_CARD))
    assert p.in_catalogue is False
    assert p.callable_now is True


def test_an_unreachable_provider_does_not_crash_the_probe() -> None:
    p = providers.probe(fetch=_fetch(catalogue=(0, "URLError: offline"), model=(0, "offline")))
    assert p.callable_now is False
    assert "catalogue unavailable" in p.note


def test_an_unreadable_catalogue_is_noted_rather_than_raised() -> None:
    p = providers.probe(fetch=_fetch(catalogue=(200, "not json")))
    assert "unreadable" in p.note
    assert p.callable_now is False
