from typing import Any

import pytest
import requests

from agent_linkdin.adapters.search.tavily import TavilyWebSearch


def test_search_without_api_key_returns_empty_context() -> None:
    adapter = TavilyWebSearch(api_key=None)

    context = adapter.search("ia générative")

    assert context.is_empty


def test_search_nominal_maps_results(monkeypatch: pytest.MonkeyPatch) -> None:
    payload = {
        "answer": "Résumé global",
        "results": [
            {
                "title": "Article A",
                "url": "https://exemple.fr/a",
                "content": "x" * 600,
                "published_date": "2026-07-01",
            }
        ],
    }

    class FakeResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict[str, Any]:
            return payload

    monkeypatch.setattr(requests, "post", lambda *args, **kwargs: FakeResponse())
    adapter = TavilyWebSearch(api_key="tvly-test")

    context = adapter.search("ia générative")

    assert context.summary == "Résumé global"
    assert len(context.results) == 1
    assert context.results[0].title == "Article A"
    assert len(context.results[0].content) == 500


def test_search_request_error_returns_empty_context(monkeypatch: pytest.MonkeyPatch) -> None:
    def raise_error(*args: Any, **kwargs: Any) -> Any:
        raise requests.ConnectionError("réseau indisponible")

    monkeypatch.setattr(requests, "post", raise_error)
    adapter = TavilyWebSearch(api_key="tvly-test")

    context = adapter.search("ia générative")

    assert context.is_empty
