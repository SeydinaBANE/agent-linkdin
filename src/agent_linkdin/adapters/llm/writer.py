import anthropic

from agent_linkdin.adapters.llm.client import message_text
from agent_linkdin.adapters.llm.prompts import DRAFT_SYSTEM_PROMPT
from agent_linkdin.domain.models import Draft, ResearchInsights


class LlmDraftWriter:
    def __init__(self, client: anthropic.Anthropic, model: str, max_tokens: int = 600) -> None:
        self._client = client
        self._model = model
        self._max_tokens = max_tokens

    def write(self, topic: str, insights: ResearchInsights, feedback: str, iteration: int) -> Draft:
        user_content = f"Topic: {topic}\n\nResearch Insights:\n{insights.content}\n"
        if feedback and iteration > 0:
            user_content += (
                "\nPrevious draft was rejected. Here's the feedback to address:\n"
                f"{feedback}\n\n"
                "Write a significantly improved version that fixes these issues.\n"
            )
        else:
            user_content += "\nWrite the LinkedIn post now."

        message = self._client.messages.create(
            model=self._model,
            max_tokens=self._max_tokens,
            system=DRAFT_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_content}],
        )
        return Draft(content=message_text(message), iteration=iteration)
