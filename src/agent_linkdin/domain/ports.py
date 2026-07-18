from typing import Protocol

from agent_linkdin.domain.models import (
    Draft,
    GeneratedPost,
    ResearchInsights,
    ReviewResult,
    SearchContext,
    StoredPost,
    Trace,
)


class WebSearchPort(Protocol):
    def search(self, query: str) -> SearchContext: ...


class ResearcherPort(Protocol):
    def research(self, topic: str, context: SearchContext) -> ResearchInsights: ...


class DraftWriterPort(Protocol):
    def write(
        self, topic: str, insights: ResearchInsights, feedback: str, iteration: int
    ) -> Draft: ...


class ReviewerPort(Protocol):
    def review(self, draft: Draft) -> ReviewResult: ...


class PostRepositoryPort(Protocol):
    def save(self, post: GeneratedPost, trace: Trace) -> StoredPost: ...
