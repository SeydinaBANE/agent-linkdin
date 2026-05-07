"""
Draft Agent — Writes hooks, structures body, matches voice
Model: Claude Sonnet 4.6 (style & speed)
"""

import anthropic
import os
from dotenv import load_dotenv
load_dotenv()

SYSTEM_PROMPT = """You are an elite LinkedIn ghostwriter. You write posts that go viral.

VOICE GUIDELINES:
- Write like a smart practitioner, not a consultant
- No corporate speak, no "I'm thrilled to announce"
- Short punchy sentences. Mix with longer ones for rhythm.
- First line = hook that stops the scroll (no question hooks, no "Hot take:")
- Use white space generously — short paragraphs of 1-3 lines
- End with ONE clear insight or call-to-action, not a list of questions

STRUCTURE:
1. Hook (1-2 lines) — surprising stat, bold statement, or counterintuitive truth
2. Context (2-3 lines) — why this matters NOW
3. Body (3-5 short paragraphs) — your insights, concrete examples
4. Closing (1-2 lines) — takeaway or perspective shift

FORMATTING RULES:
- 150-250 words total
- No hashtags in the body (add 2-3 at the very end only)
- No bullet points — write in prose
- No emojis unless one strategic one in the hook
"""


def run_draft(topic: str, insights: str, feedback: str = "", iteration: int = 0) -> str:
    client = anthropic.Anthropic(
        api_key=os.environ["OPENROUTER_API_KEY"],
        base_url="https://openrouter.ai/api",
    )

    user_content = f"""Topic: {topic}

Research Insights:
{insights}
"""

    if feedback and iteration > 0:
        user_content += f"""
Previous draft was rejected. Here's the feedback to address:
{feedback}

Write a significantly improved version that fixes these issues.
"""
    else:
        user_content += "\nWrite the LinkedIn post now."

    message = client.messages.create(
        model="anthropic/claude-haiku-4-5",
        max_tokens=600,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": user_content
            }
        ]
    )

    return message.content[0].text