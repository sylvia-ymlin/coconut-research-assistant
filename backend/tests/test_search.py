from app.core.config import Configuration
from app.services import search


class FakeSearchTool:
    def __init__(self, response):
        self._response = response

    def run(self, payload):
        return self._response


def test_dispatch_search_normalizes_text_notice(monkeypatch) -> None:
    monkeypatch.setattr(search, "_GLOBAL_SEARCH_TOOL", FakeSearchTool("rate limited"))

    payload, notices, answer_text, backend = search.dispatch_search(
        "agent frameworks",
        Configuration(search_api="duckduckgo"),
        loop_count=0,
    )

    assert payload["results"] == []
    assert notices == ["rate limited"]
    assert answer_text is None
    assert backend == "duckduckgo"


def test_dispatch_search_uses_structured_payload(monkeypatch) -> None:
    monkeypatch.setattr(
        search,
        "_GLOBAL_SEARCH_TOOL",
        FakeSearchTool(
            {
                "backend": "tavily",
                "answer": "short answer",
                "notices": ["fallback"],
                "results": [{"title": "A", "url": "https://example.com"}],
            }
        ),
    )

    payload, notices, answer_text, backend = search.dispatch_search(
        "agent frameworks",
        Configuration(search_api="tavily"),
        loop_count=1,
    )

    assert payload["results"][0]["title"] == "A"
    assert notices == ["fallback"]
    assert answer_text == "short answer"
    assert backend == "tavily"
