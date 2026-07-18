# Documentation — Agent LinkedIn

Documentation du projet, organisée selon le cadre [Diataxis](https://diataxis.fr/) : chaque document répond à un besoin de lecture différent.

## Par où commencer

| Tu veux… | Va voir |
|---|---|
| Générer ton premier post de zéro | [Tutoriel : ton premier post LinkedIn](tutoriel-premier-post.md) |
| Configurer les clés, changer de modèle, régler la boucle de réécriture | [How-to : configurer l'agent](howto-configuration.md) |
| Brancher une autre recherche web, une base de données, un autre LLM | [How-to : ajouter un adapter](howto-ajouter-un-adapter.md) |
| La liste exhaustive des commandes, variables et types | [Référence technique](reference.md) |
| Comprendre pourquoi le projet est structuré ainsi | [Explication : l'architecture hexagonale](explication-architecture.md) |

## Vue d'ensemble

L'agent génère des posts LinkedIn via un pipeline multi-agents LangGraph :

```
research → draft → review → [approuvé ?] → save
              ↑______________| (réécritures limitées par max_iterations)
```

Trois agents LLM (recherche, rédaction, revue) collaborent, avec une recherche web Tavily optionnelle en amont et une sauvegarde fichiers en aval. Le tout est organisé en architecture hexagonale : le cœur métier ne connaît ni Tavily, ni OpenRouter, ni le système de fichiers — uniquement des interfaces (« ports ») que des adapters implémentent.
