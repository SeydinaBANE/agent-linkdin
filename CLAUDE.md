# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies (uses uv)
uv sync

# Run the agent with a topic
uv run python main.py "your topic here"

# Run with default topic
uv run python main.py
```

## Environment

Requires `OPENROUTER_API_KEY` in a `.env` file. The Anthropic SDK is configured to route through OpenRouter (`base_url="https://openrouter.ai/api"`), so model names use the `anthropic/` prefix (e.g. `anthropic/claude-haiku-4-5`).

## Architecture

LangGraph pipeline in `main.py` with three agent nodes and a conditional loop:

```
research → draft → review → [approved?] → save → END
                     ↑____________| (max 2 rewrites)
```

**`AgentState`** (TypedDict in `main.py`) is the shared state that flows through all nodes. Key fields: `topic`, `research_insights`, `draft_post`, `final_post`, `review_feedback`, `approved`, `iteration`, `trace`.

**Node responsibilities:**
- `research.py` — Extracts angles, facts, unique POVs, and clichés to avoid for the topic
- `draft.py` — Writes the LinkedIn post (150–250 words, no bullets, prose only); incorporates `review_feedback` on rewrites
- `review.py` — Returns JSON `{approved, score, feedback, improved_post}`; auto-approves if JSON parse fails to break infinite loops

**Output** is written to `output/posts/<timestamp>_<slug>.md` (the post) and `output/traces/<timestamp>_<slug>.json` (timing + iteration metadata).

**Loop limit:** `MAX_ITERATIONS = 2` in `should_rewrite()` (`main.py:124`). After 2 rejections the best draft is published as-is.
