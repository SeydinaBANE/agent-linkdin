
"""
Research Agent — Scans trends and extracts insights
Model: Claude Haiku (fast & cheap for research)
"""

import anthropic
import os
from dotenv import load_dotenv
load_dotenv()


SYSTEM_PROMPT = """You are a LinkedIn research analyst. Your job is to:
1. Identify the 3-5 most relevant, current angles on the given topic
2. Extract concrete facts, stats, or observations that would resonate with a tech/business audience
3. Suggest a unique POV or contrarian take that would stand out on LinkedIn
4. Note what's been overdone on this topic (to avoid clichés)

Be specific. No fluff. Output structured insights, not generic summaries.
Format your response as:
## Key Angles
[bullet points]

## Concrete Facts/Stats
[bullet points]

## Unique POV
[1-2 sentences]

## Clichés to Avoid
[bullet points]
"""


def run_research(topic: str) -> str:
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
                "content": f"Research this topic for a LinkedIn post: **{topic}**"
            }
        ]
    )

    return message.content[0].text