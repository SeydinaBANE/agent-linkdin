from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True)
class SearchResult:
    title: str
    url: str
    content: str
    published_date: str | None = None


@dataclass(frozen=True)
class SearchContext:
    summary: str | None
    results: tuple[SearchResult, ...]

    @property
    def is_empty(self) -> bool:
        return self.summary is None and not self.results

    @classmethod
    def empty(cls) -> "SearchContext":
        return cls(summary=None, results=())


@dataclass(frozen=True)
class ResearchInsights:
    topic: str
    content: str


@dataclass(frozen=True)
class Draft:
    content: str
    iteration: int


@dataclass(frozen=True)
class ReviewResult:
    approved: bool
    feedback: str
    final_post: str


@dataclass(frozen=True)
class GeneratedPost:
    topic: str
    content: str
    approved: bool
    iterations: int
    generated_at: datetime


@dataclass(frozen=True)
class DraftTiming:
    iteration: int
    duration_s: float


@dataclass(frozen=True)
class ReviewTiming:
    iteration: int
    duration_s: float
    approved: bool


@dataclass
class Trace:
    research_duration_s: float | None = None
    drafts: list[DraftTiming] = field(default_factory=list)
    reviews: list[ReviewTiming] = field(default_factory=list)


@dataclass(frozen=True)
class StoredPost:
    post_path: Path
    trace_path: Path
