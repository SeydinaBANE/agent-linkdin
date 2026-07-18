from agent_linkdin.adapters.llm.researcher import LlmResearcher, format_search_context
from agent_linkdin.domain.models import SearchContext, SearchResult
from tests.conftest import FakeAnthropicClient


def test_format_search_context_empty_falls_back_to_model_knowledge() -> None:
    formatted = format_search_context(SearchContext.empty())

    assert "Aucun résultat" in formatted


def test_format_search_context_includes_results_and_summary() -> None:
    context = SearchContext(
        summary="Résumé",
        results=(
            SearchResult(
                title="Titre",
                url="https://exemple.fr",
                content="Extrait",
                published_date="2026-07-01",
            ),
        ),
    )

    formatted = format_search_context(context)

    assert "Résumé" in formatted
    assert "Titre" in formatted
    assert "https://exemple.fr" in formatted
    assert "2026-07-01" in formatted


def test_research_returns_insights_from_model(fake_client: FakeAnthropicClient) -> None:
    researcher = LlmResearcher(fake_client, model="anthropic/claude-haiku-4-5")  # type: ignore[arg-type]

    insights = researcher.research("agents IA", SearchContext.empty())

    assert insights.topic == "agents IA"
    assert insights.content == "réponse du modèle"
    assert fake_client.messages.calls[0]["model"] == "anthropic/claude-haiku-4-5"
