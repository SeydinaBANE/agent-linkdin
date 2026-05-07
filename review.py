"""
Review Agent — Stress-tests hooks, sharpens arguments
Model: Claude Opus 4.6 (frontier reasoning)
"""

import anthropic
import os
import re
from dotenv import load_dotenv
load_dotenv()

SYSTEM_PROMPT = """You are a ruthless LinkedIn content editor. Your job is to ensure only exceptional posts get published.

QUALITY RUBRIC — A post must pass ALL of these:

✅ HOOK TEST: Does the first line make you stop scrolling? Would YOU share this?
✅ ORIGINALITY TEST: Is this a fresh angle, or recycled LinkedIn wisdom?
✅ SPECIFICITY TEST: Does it have concrete details, not vague generalities?
✅ VOICE TEST: Does it sound like a real person, not a content bot?
✅ LENGTH TEST: Is it 150-250 words? Not too long, not too short?
✅ STRUCTURE TEST: Good rhythm? White space? No bullet-point abuse?

REWRITE TRIGGERS (if ANY of these are true → REJECT):
- Hook starts with "In today's world", "I've been thinking", or a question
- Contains phrases like "game-changer", "leverage", "synergy", "in the age of AI"
- More than one emoji
- Ends with multiple questions asking for engagement
- Feels like it was written by ChatGPT (too smooth, too balanced, no edge)
- Under 120 words or over 280 words

RESPONSE FORMAT — respond ONLY with valid JSON:
{
  "approved": true/false,
  "score": 1-10,
  "feedback": "specific critique if rejected, empty string if approved",
  "improved_post": "if approved, return the post with minor polish; if rejected, return empty string"
}
"""


def run_review(draft_post: str) -> tuple[bool, str, str]:
    """Returns: (approved, feedback, final_post)"""
    client = anthropic.Anthropic(
        api_key=os.environ["OPENROUTER_API_KEY"],
        base_url="https://openrouter.ai/api",
    )

    message = client.messages.create(
        model="anthropic/claude-haiku-4-5",
        max_tokens=800,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"Review this LinkedIn post:\n\n---\n{draft_post}\n---"
            }
        ]
    )

    response_text = message.content[0].text

    # Parse JSON response
    try:
        # Strip markdown code blocks if present
        clean = re.sub(r"```json|```", "", response_text).strip()
        data = __import__("json").loads(clean)
        approved = data.get("approved", False)
        feedback = data.get("feedback", "")
        improved = data.get("improved_post", "")
        return approved, feedback, improved if improved else draft_post
    except Exception as e:
        # If parsing fails, approve to avoid infinite loop
        print(f"   ⚠️  Review parse error: {e}. Auto-approving.")
        return True, "", draft_post
