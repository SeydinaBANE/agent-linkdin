import json
from datetime import datetime
from pathlib import Path

from agent_linkdin.adapters.persistence.file_repository import FilePostRepository, slugify
from agent_linkdin.domain.models import GeneratedPost, Trace


def test_slugify_nominal() -> None:
    assert slugify("AI Agents in Production!") == "ai_agents_in_production"


def test_slugify_empty_falls_back() -> None:
    assert slugify("***") == "post"


def test_save_writes_post_and_trace(tmp_path: Path) -> None:
    repository = FilePostRepository(tmp_path)
    post = GeneratedPost(
        topic="Agents IA",
        content="Contenu final",
        approved=True,
        iterations=2,
        generated_at=datetime(2026, 7, 18, 10, 30, 0),
    )

    stored = repository.save(post, Trace(research_duration_s=1.2))

    assert stored.post_path.exists()
    assert "Contenu final" in stored.post_path.read_text(encoding="utf-8")
    trace_data = json.loads(stored.trace_path.read_text(encoding="utf-8"))
    assert trace_data["topic"] == "Agents IA"
    assert trace_data["iterations"] == 2
    assert trace_data["trace"]["research_duration_s"] == 1.2
