# Agent LinkedIn

Pipeline multi-agents LangGraph qui recherche un sujet, rédige un post LinkedIn, et l'affine de manière itérative jusqu'à ce qu'il passe une revue qualité.

## Pipeline

```
Recherche → Rédaction → Révision → [approuvé?] → Sauvegarde
                ↑_____________| (max 2 réécritures)
```

1. **Recherche** — Identifie les angles, stats, point de vue unique et clichés à éviter sur le sujet
2. **Rédaction** — Écrit un post LinkedIn de 150–250 mots en prose (sans puces, sans jargon corporate)
3. **Révision** — Évalue le post selon une grille qualité ; le renvoie en réécriture si rejeté
4. **Sauvegarde** — Enregistre le post final dans `output/posts/` et les métriques dans `output/traces/`

## Installation

```bash
# Installer les dépendances
uv sync

# Configurer les variables d'environnement
cp .env_exemple .env
# puis remplir les clés dans .env
```

| Variable | Obligatoire | Rôle |
|---|---|---|
| `OPENROUTER_API_KEY` | Oui | Accès aux modèles Claude via [openrouter.ai](https://openrouter.ai) |
| `TAVILY_API_KEY` | Non | Recherche web réelle (résultats récents) via [tavily.com](https://tavily.com) |

Sans `TAVILY_API_KEY`, l'agent Research se base uniquement sur les connaissances du modèle.

## Utilisation

```bash
uv run python main.py "les agents IA en production en 2025"
# ou via le script installé
uv run agent-linkdin "les agents IA en production en 2025" --verbose
```

Les fichiers générés sont sauvegardés dans :
- `output/posts/<timestamp>_<slug>.md` — le post final
- `output/traces/<timestamp>_<slug>.json` — nombre d'itérations, durées, statut d'approbation

## Architecture

Architecture hexagonale (ports & adapters) sous `src/agent_linkdin/` :

```
src/agent_linkdin/
├── domain/          # Modèles immuables + ports (Protocol) — zéro dépendance externe
├── application/     # Use case GeneratePost orchestré par LangGraph (ports injectés)
├── adapters/
│   ├── search/      # Tavily (WebSearchPort)
│   ├── llm/         # Agents research/draft/review via OpenRouter (Researcher/DraftWriter/ReviewerPort)
│   └── persistence/ # Sauvegarde fichiers (PostRepositoryPort)
├── config.py        # Settings pydantic-settings (.env)
├── logging_config.py
└── cli.py           # Composition root + point d'entrée
```

## Documentation

La documentation complète est dans [`docs/`](docs/README.md) (cadre Diataxis) :

- [Tutoriel : ton premier post LinkedIn](docs/tutoriel-premier-post.md) — de l'installation au premier post généré
- [How-to : configurer l'agent](docs/howto-configuration.md) — clés, modèles, réécritures, dossiers
- [How-to : ajouter un adapter](docs/howto-ajouter-un-adapter.md) — brancher un autre moteur de recherche, LLM ou stockage
- [Référence technique](docs/reference.md) — CLI, variables d'environnement, modèles, ports, formats de sortie
- [Explication : l'architecture hexagonale](docs/explication-architecture.md) — le pourquoi du design et ses compromis

## Développement

```bash
uv run pytest         # tests (services externes mockés)
uv run ruff check src tests main.py
uv run ruff format src tests main.py
uv run mypy           # typage strict
```
