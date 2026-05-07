# CLAUDE.md

Ce fichier fournit des instructions à Claude Code (claude.ai/code) pour travailler dans ce dépôt.

## Commandes

```bash
# Installer les dépendances (utilise uv)
uv sync

# Lancer l'agent avec un sujet
uv run python main.py "ton sujet ici"

# Lancer avec le sujet par défaut
uv run python main.py
```

## Environnement

Nécessite `OPENROUTER_API_KEY` dans un fichier `.env`. Le SDK Anthropic est configuré pour passer par OpenRouter (`base_url="https://openrouter.ai/api"`), donc les noms de modèles utilisent le préfixe `anthropic/` (ex. `anthropic/claude-haiku-4-5`).

## Architecture

Pipeline LangGraph dans `main.py` avec trois nœuds agents et une boucle conditionnelle :

```
research → draft → review → [approuvé?] → save → END
                     ↑____________| (max 2 réécritures)
```

**`AgentState`** (TypedDict dans `main.py`) est l'état partagé qui circule entre tous les nœuds. Champs clés : `topic`, `research_insights`, `draft_post`, `final_post`, `review_feedback`, `approved`, `iteration`, `trace`.

**Responsabilités des nœuds :**
- `research.py` — Extrait les angles, faits, points de vue uniques et clichés à éviter pour le sujet
- `draft.py` — Rédige le post LinkedIn (150–250 mots, sans puces, en prose) ; intègre `review_feedback` lors des réécritures
- `review.py` — Retourne un JSON `{approved, score, feedback, improved_post}` ; approuve automatiquement si le parsing JSON échoue pour éviter les boucles infinies

**Les fichiers de sortie** sont écrits dans `output/posts/<timestamp>_<slug>.md` (le post) et `output/traces/<timestamp>_<slug>.json` (durées + métadonnées d'itération).

**Limite de boucle :** `MAX_ITERATIONS = 2` dans `should_rewrite()` (`main.py:124`). Après 2 rejets, le meilleur brouillon est publié tel quel.
