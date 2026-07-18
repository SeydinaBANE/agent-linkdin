import anthropic

from agent_linkdin.adapters.llm.client import message_text
from agent_linkdin.adapters.llm.prompts import RESEARCH_SYSTEM_PROMPT
from agent_linkdin.domain.models import ResearchInsights, SearchContext


def format_search_context(context: SearchContext) -> str:
    if context.is_empty:
        return "Aucun résultat de recherche disponible. Utilise tes connaissances générales."

    formatted = "=== RÉSULTATS DE RECHERCHE WEB ===\n\n"
    if context.summary:
        formatted += f"**Résumé :**\n{context.summary}\n\n"
    for i, result in enumerate(context.results, 1):
        formatted += f"**Article {i} :** {result.title}\n"
        if result.published_date:
            formatted += f"Date : {result.published_date}\n"
        formatted += f"URL : {result.url}\nExtrait : {result.content}\n\n"
    return formatted


class LlmResearcher:
    def __init__(self, client: anthropic.Anthropic, model: str, max_tokens: int = 1000) -> None:
        self._client = client
        self._model = model
        self._max_tokens = max_tokens

    def research(self, topic: str, context: SearchContext) -> ResearchInsights:
        message = self._client.messages.create(
            model=self._model,
            max_tokens=self._max_tokens,
            system=RESEARCH_SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Sujet LinkedIn : **{topic}**\n\n"
                        f"{format_search_context(context)}\n\n"
                        "Analyse ces résultats et produis les insights."
                    ),
                }
            ],
        )
        return ResearchInsights(topic=topic, content=message_text(message))
