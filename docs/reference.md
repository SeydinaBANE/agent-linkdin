# Référence technique

Description exhaustive de la surface publique du projet : CLI, configuration, domaine, sorties.

## CLI

```
uv run agent-linkdin [topic ...] [--verbose]
uv run python main.py [topic ...] [--verbose]
```

| Argument | Type | Défaut | Effet |
|---|---|---|---|
| `topic` | positionnel, mots multiples | `"AI agents in production 2025"` | Sujet du post ; les mots sont joints par des espaces |
| `--verbose` | flag | désactivé | Logs au niveau DEBUG au lieu de INFO |

Codes de retour : `0` succès, `1` configuration invalide ou échec de génération (détail dans les logs, écrits sur stderr).

Le point d'entrée est `agent_linkdin.cli:main` (script installé `agent-linkdin`) ; `main.py` à la racine est un wrapper de compatibilité.

## Configuration (`Settings`)

Source : `src/agent_linkdin/config.py`. Chargée depuis `.env` (encodage UTF-8) et l'environnement ; les variables d'environnement priment sur `.env`. Variables inconnues ignorées.

| Variable | Type | Défaut | Rôle |
|---|---|---|---|
| `OPENROUTER_API_KEY` | `str` | — (obligatoire, `ValueError` si vide) | Clé OpenRouter pour les trois agents LLM |
| `TAVILY_API_KEY` | `str \| None` | `None` | Clé Tavily ; recherche web désactivée si absente |
| `OPENROUTER_BASE_URL` | `str` | `https://openrouter.ai/api` | URL de base du SDK Anthropic |
| `TAVILY_BASE_URL` | `str` | `https://api.tavily.com` | URL de base de l'API Tavily |
| `RESEARCH_MODEL` | `str` | `anthropic/claude-haiku-4-5` | Modèle de l'agent recherche |
| `DRAFT_MODEL` | `str` | `anthropic/claude-haiku-4-5` | Modèle de l'agent rédaction |
| `REVIEW_MODEL` | `str` | `anthropic/claude-haiku-4-5` | Modèle de l'agent revue |
| `OUTPUT_DIR` | `Path` | `output` | Racine des sorties (`posts/`, `traces/`) |
| `MAX_ITERATIONS` | `int` | `2` | Nombre maximal de réécritures après rejet (brouillons max = `MAX_ITERATIONS + 1`) |
| `SEARCH_MAX_RESULTS` | `int` | `5` | Nombre de résultats demandés à Tavily |
| `SEARCH_TIMEOUT_S` | `float` | `15.0` | Timeout HTTP Tavily en secondes |

## Domaine

Source : `src/agent_linkdin/domain/`.

### Modèles (`models.py`)

Toutes les dataclasses sont immuables (`frozen=True`) sauf `Trace`.

| Modèle | Champs |
|---|---|
| `SearchResult` | `title: str`, `url: str`, `content: str` (tronqué à 500 caractères par l'adapter Tavily), `published_date: str \| None` |
| `SearchContext` | `summary: str \| None`, `results: tuple[SearchResult, ...]` ; propriété `is_empty`, constructeur `SearchContext.empty()` |
| `ResearchInsights` | `topic: str`, `content: str` |
| `Draft` | `content: str`, `iteration: int` (0 = premier brouillon) |
| `ReviewResult` | `approved: bool`, `feedback: str`, `final_post: str` (post poli si approuvé, sinon le brouillon tel quel) |
| `GeneratedPost` | `topic: str`, `content: str`, `approved: bool`, `iterations: int` (nombre de brouillons produits), `generated_at: datetime` |
| `DraftTiming` | `iteration: int`, `duration_s: float` |
| `ReviewTiming` | `iteration: int`, `duration_s: float`, `approved: bool` |
| `Trace` | `research_duration_s: float \| None`, `drafts: list[DraftTiming]`, `reviews: list[ReviewTiming]` |
| `StoredPost` | `post_path: Path`, `trace_path: Path` |

### Ports (`ports.py`)

Interfaces en `typing.Protocol` — satisfaction structurelle, pas d'héritage :

```python
class WebSearchPort(Protocol):
    def search(self, query: str) -> SearchContext: ...

class ResearcherPort(Protocol):
    def research(self, topic: str, context: SearchContext) -> ResearchInsights: ...

class DraftWriterPort(Protocol):
    def write(self, topic: str, insights: ResearchInsights, feedback: str, iteration: int) -> Draft: ...

class ReviewerPort(Protocol):
    def review(self, draft: Draft) -> ReviewResult: ...

class PostRepositoryPort(Protocol):
    def save(self, post: GeneratedPost, trace: Trace) -> StoredPost: ...
```

## Application

Source : `src/agent_linkdin/application/generate_post.py`.

`GeneratePostUseCase(web_search, researcher, writer, reviewer, repository, max_iterations=2)` — construit et compile le graphe LangGraph au constructeur.

`execute(topic: str) -> GenerationReport` — lance le pipeline et renvoie `GenerationReport(post: GeneratedPost, stored: StoredPost, trace: Trace)`. Lève `RuntimeError` si le pipeline se termine dans un état incohérent.

Requête envoyée au moteur de recherche : `"{topic} 2025 tendances actualité"`.

## Sorties fichiers

Écrites par `FilePostRepository` (`adapters/persistence/file_repository.py`). Le slug est le sujet en minuscules, caractères non `[a-z0-9]` remplacés par `_`, tronqué à 30 caractères (`"post"` si vide).

**`output/posts/<AAAAMMJJ_HHMMSS>_<slug>.md`** :

```markdown
# LinkedIn Post — <topic>
*Generated: <ISO 8601>*

---

<contenu du post>
```

**`output/traces/<AAAAMMJJ_HHMMSS>_<slug>.json`** :

```json
{
  "topic": "…",
  "iterations": 2,
  "approved": true,
  "trace": {
    "research_duration_s": 4.2,
    "drafts": [{"iteration": 1, "duration_s": 3.1}],
    "reviews": [{"iteration": 1, "duration_s": 2.4, "approved": true}]
  },
  "generated_at": "2026-07-18T14:30:12.000000"
}
```

## Commandes de développement

| Commande | Effet |
|---|---|
| `uv sync` | Installe dépendances + paquet en mode éditable |
| `uv run pytest` | Tests (aucun appel réseau, tout est mocké) |
| `uv run ruff check src tests main.py` | Lint (`E`, `F`, `I`, `UP`, `B`, `SIM`, `ANN`, ligne ≤ 100) |
| `uv run ruff format src tests main.py` | Formatage |
| `uv run mypy` | Typage strict sur le paquet `agent_linkdin` |

## Voir aussi

- [How-to : configurer l'agent](howto-configuration.md)
- [How-to : ajouter un adapter](howto-ajouter-un-adapter.md)
- [Explication : l'architecture hexagonale](explication-architecture.md)
