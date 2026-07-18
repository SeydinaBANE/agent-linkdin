import logging
from typing import Any

import requests

from agent_linkdin.domain.models import SearchContext, SearchResult

logger = logging.getLogger(__name__)


class TavilyWebSearch:
    def __init__(
        self,
        api_key: str | None,
        base_url: str = "https://api.tavily.com",
        max_results: int = 5,
        timeout_s: float = 15.0,
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._max_results = max_results
        self._timeout_s = timeout_s

    def search(self, query: str) -> SearchContext:
        if not self._api_key:
            logger.warning("TAVILY_API_KEY absente — recherche web désactivée")
            return SearchContext.empty()

        try:
            response = requests.post(
                f"{self._base_url}/search",
                json={
                    "api_key": self._api_key,
                    "query": query,
                    "max_results": self._max_results,
                    "search_depth": "advanced",
                    "include_answer": True,
                    "include_raw_content": False,
                },
                timeout=self._timeout_s,
            )
            response.raise_for_status()
            data: dict[str, Any] = response.json()
        except requests.RequestException as exc:
            logger.warning("Erreur Tavily : %s", exc)
            return SearchContext.empty()

        results = tuple(
            SearchResult(
                title=str(item.get("title", "")),
                url=str(item.get("url", "")),
                content=str(item.get("content", ""))[:500],
                published_date=item.get("published_date") or None,
            )
            for item in data.get("results", [])
        )
        summary = data.get("answer") or None

        logger.info("%d résultats trouvés via Tavily", len(results))
        return SearchContext(summary=summary, results=results)
