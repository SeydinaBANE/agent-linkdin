from pathlib import Path

from agent_linkdin.application.generate_post import GeneratePostUseCase
from agent_linkdin.domain.models import (
    Draft,
    GeneratedPost,
    ResearchInsights,
    ReviewResult,
    SearchContext,
    StoredPost,
    Trace,
)


class StubWebSearch:
    def search(self, query: str) -> SearchContext:
        return SearchContext.empty()


class StubResearcher:
    def research(self, topic: str, context: SearchContext) -> ResearchInsights:
        return ResearchInsights(topic=topic, content="insights")


class StubWriter:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def write(self, topic: str, insights: ResearchInsights, feedback: str, iteration: int) -> Draft:
        self.calls.append(feedback)
        return Draft(content=f"brouillon v{iteration + 1}", iteration=iteration)


class StubReviewer:
    def __init__(self, verdicts: list[bool]) -> None:
        self._verdicts = verdicts
        self._index = 0

    def review(self, draft: Draft) -> ReviewResult:
        approved = self._verdicts[min(self._index, len(self._verdicts) - 1)]
        self._index += 1
        feedback = "" if approved else "à retravailler"
        return ReviewResult(approved=approved, feedback=feedback, final_post=draft.content)


class StubRepository:
    def __init__(self) -> None:
        self.saved: list[GeneratedPost] = []

    def save(self, post: GeneratedPost, trace: Trace) -> StoredPost:
        self.saved.append(post)
        return StoredPost(post_path=Path("post.md"), trace_path=Path("trace.json"))


def build_use_case(
    verdicts: list[bool], max_iterations: int = 2
) -> tuple[GeneratePostUseCase, StubWriter, StubRepository]:
    writer = StubWriter()
    repository = StubRepository()
    use_case = GeneratePostUseCase(
        web_search=StubWebSearch(),
        researcher=StubResearcher(),
        writer=writer,
        reviewer=StubReviewer(verdicts),
        repository=repository,
        max_iterations=max_iterations,
    )
    return use_case, writer, repository


def test_execute_approved_first_pass() -> None:
    use_case, writer, repository = build_use_case([True])

    report = use_case.execute("agents IA")

    assert report.post.approved
    assert report.post.iterations == 1
    assert len(writer.calls) == 1
    assert len(repository.saved) == 1
    assert report.trace.reviews[0].approved


def test_execute_rejected_then_approved_passes_feedback() -> None:
    use_case, writer, _ = build_use_case([False, True])

    report = use_case.execute("agents IA")

    assert report.post.approved
    assert report.post.iterations == 2
    assert writer.calls == ["", "à retravailler"]


def test_execute_always_rejected_stops_at_max_iterations() -> None:
    use_case, writer, repository = build_use_case([False], max_iterations=2)

    report = use_case.execute("agents IA")

    assert not report.post.approved
    assert report.post.iterations == 3
    assert len(writer.calls) == 3
    assert repository.saved[0].content == "brouillon v3"
