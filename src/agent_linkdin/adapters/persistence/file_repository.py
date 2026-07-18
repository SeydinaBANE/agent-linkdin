import json
import logging
import re
from dataclasses import asdict
from pathlib import Path

from agent_linkdin.domain.models import GeneratedPost, StoredPost, Trace

logger = logging.getLogger(__name__)


def slugify(text: str, max_length: int = 30) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
    return slug[:max_length] or "post"


class FilePostRepository:
    def __init__(self, output_dir: Path) -> None:
        self._posts_dir = output_dir / "posts"
        self._traces_dir = output_dir / "traces"

    def save(self, post: GeneratedPost, trace: Trace) -> StoredPost:
        self._posts_dir.mkdir(parents=True, exist_ok=True)
        self._traces_dir.mkdir(parents=True, exist_ok=True)

        ts = post.generated_at.strftime("%Y%m%d_%H%M%S")
        slug = slugify(post.topic)

        post_path = self._posts_dir / f"{ts}_{slug}.md"
        post_path.write_text(
            f"# LinkedIn Post — {post.topic}\n"
            f"*Generated: {post.generated_at.isoformat()}*\n\n---\n\n"
            f"{post.content}",
            encoding="utf-8",
        )

        trace_path = self._traces_dir / f"{ts}_{slug}.json"
        trace_path.write_text(
            json.dumps(
                {
                    "topic": post.topic,
                    "iterations": post.iterations,
                    "approved": post.approved,
                    "trace": asdict(trace),
                    "generated_at": post.generated_at.isoformat(),
                },
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        logger.info("Post sauvegardé : %s", post_path)
        logger.info("Trace sauvegardée : %s", trace_path)
        return StoredPost(post_path=post_path, trace_path=trace_path)
