from agent_linkdin.adapters.llm.writer import LlmDraftWriter
from agent_linkdin.domain.models import ResearchInsights
from tests.conftest import FakeAnthropicClient

INSIGHTS = ResearchInsights(topic="agents IA", content="insights de recherche")


def test_write_first_iteration_ignores_feedback(fake_client: FakeAnthropicClient) -> None:
    writer = LlmDraftWriter(fake_client, model="m")  # type: ignore[arg-type]

    draft = writer.write("agents IA", INSIGHTS, feedback="ignoré", iteration=0)

    assert draft.iteration == 0
    prompt = fake_client.messages.calls[0]["messages"][0]["content"]
    assert "rejected" not in prompt
    assert "insights de recherche" in prompt


def test_write_rewrite_includes_feedback(fake_client: FakeAnthropicClient) -> None:
    writer = LlmDraftWriter(fake_client, model="m")  # type: ignore[arg-type]

    draft = writer.write("agents IA", INSIGHTS, feedback="Hook trop faible", iteration=1)

    assert draft.iteration == 1
    prompt = fake_client.messages.calls[0]["messages"][0]["content"]
    assert "Hook trop faible" in prompt
