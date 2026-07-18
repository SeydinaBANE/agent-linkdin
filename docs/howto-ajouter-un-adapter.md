# How to : ajouter un adapter

Comment brancher une nouvelle implémentation derrière un port existant — par exemple remplacer Tavily par un autre moteur de recherche, ou sauvegarder les posts en base de données au lieu du système de fichiers.

## Prérequis

- Le projet installé avec le groupe dev (`uv sync`)
- Avoir lu les signatures des ports dans `src/agent_linkdin/domain/ports.py`

Le principe : le cœur (domaine + application) ne dépend que des ports (`typing.Protocol`). Un adapter est une classe qui satisfait structurellement l'un de ces protocols — pas d'héritage requis. La composition root (`src/agent_linkdin/cli.py`) est le seul endroit où l'on choisit quelle implémentation injecter.

## Étapes (exemple : recherche web via Brave au lieu de Tavily)

1. Crée le module de l'adapter :

   ```bash
   touch src/agent_linkdin/adapters/search/brave.py
   ```

2. Implémente le protocol `WebSearchPort` — une seule méthode, `search(query: str) -> SearchContext` :

   ```python
   import requests

   from agent_linkdin.domain.models import SearchContext, SearchResult


   class BraveWebSearch:
       def __init__(self, api_key: str | None, timeout_s: float = 15.0) -> None:
           self._api_key = api_key
           self._timeout_s = timeout_s

       def search(self, query: str) -> SearchContext:
           if not self._api_key:
               return SearchContext.empty()
           response = requests.get(
               "https://api.search.brave.com/res/v1/web/search",
               params={"q": query},
               headers={"X-Subscription-Token": self._api_key},
               timeout=self._timeout_s,
           )
           response.raise_for_status()
           results = tuple(
               SearchResult(title=r["title"], url=r["url"], content=r["description"])
               for r in response.json().get("web", {}).get("results", [])
           )
           return SearchContext(summary=None, results=results)
   ```

   Règle du projet : en cas de clé absente ou d'erreur réseau, renvoie `SearchContext.empty()` plutôt que de faire échouer le pipeline (voir `tavily.py` pour le modèle à suivre).

3. Ajoute la clé dans `Settings` (`src/agent_linkdin/config.py`) :

   ```python
   brave_api_key: str | None = None
   ```

4. Injecte l'adapter dans la composition root (`src/agent_linkdin/cli.py`, fonction `build_use_case`) :

   ```python
   web_search=BraveWebSearch(api_key=settings.brave_api_key),
   ```

   Rien d'autre ne change : le use case, le domaine et les autres adapters ne sont pas touchés.

5. Écris les tests (obligatoire — un cas nominal + un cas d'erreur, réseau mocké) :

   ```bash
   touch tests/test_brave.py
   ```

   Inspire-toi de `tests/test_tavily.py` : `monkeypatch` sur `requests.get`, aucune requête réelle.

## Les autres ports

| Port | Méthode à implémenter | Adapter existant à imiter |
|---|---|---|
| `WebSearchPort` | `search(query) -> SearchContext` | `adapters/search/tavily.py` |
| `ResearcherPort` | `research(topic, context) -> ResearchInsights` | `adapters/llm/researcher.py` |
| `DraftWriterPort` | `write(topic, insights, feedback, iteration) -> Draft` | `adapters/llm/writer.py` |
| `ReviewerPort` | `review(draft) -> ReviewResult` | `adapters/llm/reviewer.py` |
| `PostRepositoryPort` | `save(post, trace) -> StoredPost` | `adapters/persistence/file_repository.py` |

## Vérification

```bash
uv run pytest
uv run ruff check src tests main.py
uv run mypy
uv run agent-linkdin "sujet de test" --verbose
```

mypy en mode strict vérifie que ta classe satisfait bien le protocol au point d'injection — une signature incompatible échoue à la compilation, pas en production.

## Dépannage

| Symptôme | Cause | Correction |
|---|---|---|
| mypy : `Argument "web_search" ... incompatible type` | La signature de ta méthode ne correspond pas au protocol | Compare champ à champ avec `domain/ports.py` (noms, types, retour) |
| Ton adapter n'est jamais appelé | Il n'est pas injecté | Vérifie `build_use_case()` dans `cli.py` |
| Le pipeline plante sur une erreur réseau | Ton adapter propage l'exception | Attrape les erreurs réseau et renvoie une valeur dégradée, comme `tavily.py` |

## Voir aussi

- [Référence technique](reference.md) — signatures complètes des ports et des modèles
- [Explication : l'architecture hexagonale](explication-architecture.md) — pourquoi l'injection se fait dans la composition root
