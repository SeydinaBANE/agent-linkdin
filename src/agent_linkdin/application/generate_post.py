import logging
import time
from dataclasses import dataclass
from datetime import datetime
from typing import TypedDict

from langgraph.graph import END, StateGraph

from agent_linkdin.domain.models import (
    Draft,
    DraftTiming,
    GeneratedPost,
    ResearchInsights,
    ReviewResult,
    ReviewTiming,
    StoredPost,
    Trace,
)
from agent_linkdin.domain.ports import (
    DraftWriterPort,
    PostRepositoryPort,
    ResearcherPort,
    ReviewerPort,
    WebSearchPort,
)

logger = logging.getLogger(__name__)


class PipelineState(TypedDict):
    topic: str
    insights: ResearchInsights | None
    draft: Draft | None
    review: ReviewResult | None
    iteration: int
    trace: Trace
    stored: StoredPost | None


@dataclass(frozen=True)
class GenerationReport:
    post: GeneratedPost
    stored: StoredPost
    trace: Trace


class GeneratePostUseCase:
    def __init__(
        self,
        web_search: WebSearchPort,
        researcher: ResearcherPort,
        writer: DraftWriterPort,
        reviewer: ReviewerPort,
        repository: PostRepositoryPort,
        max_iterations: int = 2,
    ) -> None:
        self._web_search = web_search
        self._researcher = researcher
        self._writer = writer
        self._reviewer = reviewer
        self._repository = repository
        self._max_iterations = max_iterations
        self._graph = self._build_graph()

    def execute(self, topic: str) -> GenerationReport:
        logger.info("Génération d'un post LinkedIn sur : %s", topic)
        initial: PipelineState = {
            "topic": topic,
            "insights": None,
            "draft": None,
            "review": None,
            "iteration": 0,
            "trace": Trace(),
            "stored": None,
        }
        final = self._graph.invoke(initial)
        review = final["review"]
        stored = final["stored"]
        if review is None or stored is None:
            raise RuntimeError("Pipeline terminé sans review ou sans sauvegarde")
        post = GeneratedPost(
            topic=topic,
            content=review.final_post,
            approved=review.approved,
            iterations=len(final["trace"].drafts),
            generated_at=datetime.now(),
        )
        return GenerationReport(post=post, stored=stored, trace=final["trace"])

    def _build_graph(self) -> object:
        graph: StateGraph = StateGraph(PipelineState)
        graph.add_node("research", self._research_node)
        graph.add_node("draft", self._draft_node)
        graph.add_node("review", self._review_node)
        graph.add_node("save", self._save_node)
        graph.set_entry_point("research")
        graph.add_edge("research", "draft")
        graph.add_edge("draft", "review")
        graph.add_conditional_edges(
            "review", self._should_rewrite, {"draft": "draft", "save": "save"}
        )
        graph.add_edge("save", END)
        return graph.compile()

    def _research_node(self, state: PipelineState) -> PipelineState:
        logger.info("[RESEARCH] Analyse des tendances : %s", state["topic"])
        start = time.perf_counter()
        context = self._web_search.search(f"{state['topic']} 2025 tendances actualité")
        insights = self._researcher.research(state["topic"], context)
        state["insights"] = insights
        state["trace"].research_duration_s = round(time.perf_counter() - start, 2)
        logger.info("[RESEARCH] Terminé en %.1fs", state["trace"].research_duration_s)
        return state

    def _draft_node(self, state: PipelineState) -> PipelineState:
        iteration = state["iteration"]
        logger.info("[DRAFT] Rédaction (itération %d)", iteration + 1)
        start = time.perf_counter()
        insights = state["insights"]
        if insights is None:
            raise RuntimeError("Recherche absente avant la rédaction")
        feedback = state["review"].feedback if state["review"] else ""
        draft = self._writer.write(state["topic"], insights, feedback, iteration)
        state["draft"] = draft
        state["trace"].drafts.append(
            DraftTiming(iteration=iteration + 1, duration_s=round(time.perf_counter() - start, 2))
        )
        return state

    def _review_node(self, state: PipelineState) -> PipelineState:
        logger.info("[REVIEW] Évaluation du brouillon")
        start = time.perf_counter()
        draft = state["draft"]
        if draft is None:
            raise RuntimeError("Brouillon absent avant la review")
        result = self._reviewer.review(draft)
        state["review"] = result
        state["trace"].reviews.append(
            ReviewTiming(
                iteration=state["iteration"] + 1,
                duration_s=round(time.perf_counter() - start, 2),
                approved=result.approved,
            )
        )
        if not result.approved:
            state["iteration"] += 1
        logger.info("[REVIEW] %s", "Approuvé" if result.approved else "Réécriture demandée")
        return state

    def _should_rewrite(self, state: PipelineState) -> str:
        review = state["review"]
        if review is not None and review.approved:
            return "save"
        if state["iteration"] > self._max_iterations:
            logger.warning(
                "Maximum d'itérations atteint (%d) — publication du meilleur brouillon",
                self._max_iterations,
            )
            return "save"
        return "draft"

    def _save_node(self, state: PipelineState) -> PipelineState:
        review = state["review"]
        if review is None:
            raise RuntimeError("Review absente avant la sauvegarde")
        post = GeneratedPost(
            topic=state["topic"],
            content=review.final_post,
            approved=review.approved,
            iterations=len(state["trace"].drafts),
            generated_at=datetime.now(),
        )
        state["stored"] = self._repository.save(post, state["trace"])
        return state
