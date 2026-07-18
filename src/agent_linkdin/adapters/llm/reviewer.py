import json
import logging
import re

import anthropic

from agent_linkdin.adapters.llm.client import message_text
from agent_linkdin.adapters.llm.prompts import REVIEW_SYSTEM_PROMPT
from agent_linkdin.domain.models import Draft, ReviewResult

logger = logging.getLogger(__name__)


class LlmReviewer:
    def __init__(self, client: anthropic.Anthropic, model: str, max_tokens: int = 800) -> None:
        self._client = client
        self._model = model
        self._max_tokens = max_tokens

    def review(self, draft: Draft) -> ReviewResult:
        message = self._client.messages.create(
            model=self._model,
            max_tokens=self._max_tokens,
            system=REVIEW_SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": f"Review this LinkedIn post:\n\n---\n{draft.content}\n---",
                }
            ],
        )
        return parse_review_response(message_text(message), draft)


def parse_review_response(response_text: str, draft: Draft) -> ReviewResult:
    try:
        clean = re.sub(r"```json|```", "", response_text).strip()
        data = json.loads(clean)
        approved = bool(data.get("approved", False))
        feedback = str(data.get("feedback", ""))
        improved = str(data.get("improved_post", ""))
        return ReviewResult(
            approved=approved,
            feedback=feedback,
            final_post=improved if improved else draft.content,
        )
    except (json.JSONDecodeError, AttributeError) as exc:
        logger.warning("Réponse review illisible (%s) — approbation automatique", exc)
        return ReviewResult(approved=True, feedback="", final_post=draft.content)
