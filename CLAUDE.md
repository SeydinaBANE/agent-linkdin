# CLAUDE.md

Ce fichier fournit des instructions à Claude Code (claude.ai/code) pour travailler dans ce dépôt.

## Commandes

```bash
# Installer les dépendances (utilise uv)
uv sync

# Lancer l'agent avec un sujet
uv run python main.py "ton sujet ici"
# ou
uv run agent-linkdin "ton sujet ici" [--verbose]

# Qualité (tout doit être vert avant de rendre la main)
uv run pytest
uv run ruff check src tests main.py
uv run ruff format src tests main.py
uv run mypy
```

## Environnement

Copie `.env_exemple` en `.env` et remplis les clés. La config est chargée par pydantic-settings (`src/agent_linkdin/config.py`) :

| Variable | Obligatoire | Rôle |
|---|---|---|
| `OPENROUTER_API_KEY` | Oui | Accès aux modèles Claude via OpenRouter |
| `TAVILY_API_KEY` | Non | Recherche web réelle dans l'agent Research |

Le SDK Anthropic est configuré pour passer par OpenRouter (`base_url="https://openrouter.ai/api"`), donc les noms de modèles utilisent le préfixe `anthropic/` (ex. `anthropic/claude-haiku-4-5`). Les modèles, l'URL de base, `max_iterations` et le dossier de sortie sont surchargables via variables d'environnement (voir `Settings`).

Sans `TAVILY_API_KEY`, l'agent Research fonctionne mais se base uniquement sur les connaissances du modèle (pas de données web récentes).

## Architecture

Architecture hexagonale (ports & adapters) sous `src/agent_linkdin/` :

- **`domain/`** — cœur métier sans dépendance externe. `models.py` : dataclasses immuables (`SearchContext`, `ResearchInsights`, `Draft`, `ReviewResult`, `GeneratedPost`, `Trace`, `StoredPost`). `ports.py` : interfaces en `typing.Protocol` (`WebSearchPort`, `ResearcherPort`, `DraftWriterPort`, `ReviewerPort`, `PostRepositoryPort`).
- **`application/generate_post.py`** — `GeneratePostUseCase` : orchestration LangGraph `research → draft → review → [approuvé?] → save`, avec boucle de réécriture. Les ports sont injectés au constructeur. L'incrément d'itération se fait dans le nœud review (jamais dans le routeur : LangGraph ne persiste pas les mutations faites dans les fonctions de routage).
- **`adapters/`** — implémentations concrètes : `search/tavily.py` (repli silencieux sur un contexte vide si clé absente ou erreur réseau), `llm/` (client OpenRouter + agents research/draft/review, prompts dans `prompts.py`, la review approuve automatiquement si le JSON est illisible pour éviter les boucles infinies), `persistence/file_repository.py` (écrit `output/posts/*.md` et `output/traces/*.json`).
- **`cli.py`** — composition root : construit les adapters depuis `Settings` et lance le use case. `main.py` à la racine n'est qu'un wrapper de compatibilité.

**Limite de boucle :** `max_iterations` (défaut 2) dans `Settings` ; après épuisement, le meilleur brouillon est publié tel quel.

## Tests

Pytest dans `tests/`, aucun appel réseau : Tavily est mocké via `monkeypatch` sur `requests.post`, les LLM via `FakeAnthropicClient` (`tests/conftest.py`), le use case via des stubs de ports. Nommage `test_<fonction>_<cas>`.
