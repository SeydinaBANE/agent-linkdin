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

# Ajouter ta clé API OpenRouter
echo "OPENROUTER_API_KEY=ta_clé_ici" > .env
```

Obtiens une clé API sur [openrouter.ai](https://openrouter.ai).

## Utilisation

```bash
uv run python main.py "les agents IA en production en 2025"
```

Les fichiers générés sont sauvegardés dans :
- `output/posts/<timestamp>_<slug>.md` — le post final
- `output/traces/<timestamp>_<slug>.json` — nombre d'itérations, durées, statut d'approbation
