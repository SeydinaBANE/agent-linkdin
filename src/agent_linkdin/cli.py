import argparse
import logging

from agent_linkdin.adapters.llm.client import build_client
from agent_linkdin.adapters.llm.researcher import LlmResearcher
from agent_linkdin.adapters.llm.reviewer import LlmReviewer
from agent_linkdin.adapters.llm.writer import LlmDraftWriter
from agent_linkdin.adapters.persistence.file_repository import FilePostRepository
from agent_linkdin.adapters.search.tavily import TavilyWebSearch
from agent_linkdin.application.generate_post import GeneratePostUseCase, GenerationReport
from agent_linkdin.config import Settings, load_settings
from agent_linkdin.logging_config import configure_logging

logger = logging.getLogger(__name__)

DEFAULT_TOPIC = "AI agents in production 2025"


def build_use_case(settings: Settings) -> GeneratePostUseCase:
    client = build_client(settings.openrouter_api_key, settings.openrouter_base_url)
    return GeneratePostUseCase(
        web_search=TavilyWebSearch(
            api_key=settings.tavily_api_key,
            base_url=settings.tavily_base_url,
            max_results=settings.search_max_results,
            timeout_s=settings.search_timeout_s,
        ),
        researcher=LlmResearcher(client, settings.research_model),
        writer=LlmDraftWriter(client, settings.draft_model),
        reviewer=LlmReviewer(client, settings.review_model),
        repository=FilePostRepository(settings.output_dir),
        max_iterations=settings.max_iterations,
    )


def print_report(report: GenerationReport) -> None:
    print(f"\n{'=' * 55}")
    print("  ✨ POST FINAL")
    print(f"{'=' * 55}")
    print(report.post.content)
    print(f"\n  Itérations : {report.post.iterations}")
    print(f"  Post : {report.stored.post_path}")
    print(f"  Trace : {report.stored.trace_path}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Génère un post LinkedIn sur un sujet donné")
    parser.add_argument("topic", nargs="*", help="Sujet du post")
    parser.add_argument("--verbose", action="store_true", help="Logs de debug")
    args = parser.parse_args()

    configure_logging(logging.DEBUG if args.verbose else logging.INFO)
    topic = " ".join(args.topic) if args.topic else DEFAULT_TOPIC

    try:
        settings = load_settings()
    except Exception:
        logger.exception("Configuration invalide — vérifie ton fichier .env")
        return 1

    try:
        report = build_use_case(settings).execute(topic)
    except Exception:
        logger.exception("Échec de la génération du post")
        return 1

    print_report(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
