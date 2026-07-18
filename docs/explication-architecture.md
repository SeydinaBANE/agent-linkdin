# Explication : l'architecture hexagonale

Pourquoi ce projet sépare strictement le métier (générer un bon post LinkedIn via une boucle recherche-rédaction-revue) des détails techniques (Tavily, OpenRouter, le système de fichiers), et ce que ce choix coûte.

## Le problème

La première version du projet mélangeait tout : chaque agent (`research.py`, `draft.py`, `review.py`) créait son propre client HTTP, lisait les variables d'environnement, écrivait sur stdout avec `print`, et la logique d'orchestration manipulait directement `os.makedirs` et `open()`. Conséquences concrètes :

- **Intestable sans réseau** : impossible de vérifier la boucle de réécriture sans payer des appels OpenRouter réels.
- **Couplage fournisseur** : changer Tavily pour un autre moteur de recherche demandait de toucher la logique de recherche elle-même.
- **Bug invisible** : la fonction de routage LangGraph mutait le compteur d'itérations — mutation que LangGraph ne persiste pas. La boucle de réécriture était en réalité infinie sur ce chemin, et sans tests, personne ne l'avait vu.

## L'approche

Architecture hexagonale (aussi appelée « ports & adapters ») : le cœur définit des interfaces, l'extérieur les implémente, et un unique point d'assemblage les connecte.

```
                    ┌─────────────────────────────────────┐
                    │            cli.py                    │
                    │        (composition root)            │
                    │  construit les adapters, les injecte │
                    └───────────────┬─────────────────────┘
                                    │
        ┌───────────────────────────▼──────────────────────────┐
        │        application/generate_post.py                   │
        │  GeneratePostUseCase — graphe LangGraph               │
        │  research → draft → review → [approuvé ?] → save      │
        │            ↑____________________|                     │
        └───────┬───────────────────────────────────────┬──────┘
                │ dépend uniquement des ports (Protocol) │
        ┌───────▼───────────┐                   ┌────────▼─────────┐
        │   domain/          │                   │   adapters/      │
        │  models.py (data)  │◄──implémentent────│  tavily, llm/*,  │
        │  ports.py (interf.)│                   │  file_repository │
        └────────────────────┘                   └──────────────────┘
```

- **`domain/`** ne dépend de rien d'externe : des dataclasses immuables et des `typing.Protocol`. On peut le lire en entier sans connaître Tavily ni LangGraph.
- **`application/`** orchestre le pipeline en ne parlant qu'aux ports. LangGraph y vit comme outil d'orchestration, pas comme détail exposé au reste du code.
- **`adapters/`** contient tout ce qui touche le monde extérieur. Chaque adapter est remplaçable isolément.
- **`cli.py`** est le seul endroit qui connaît à la fois la config et les implémentations concrètes.

Ce découpage a immédiatement payé : les tests du use case avec des stubs de ports ont révélé le bug de la boucle infinie (voir plus bas) le jour même du refactoring.

## Décisions notables et leurs raisons

**Des `Protocol` plutôt que des classes abstraites.** La satisfaction est structurelle : un adapter n'importe rien du domaine pour « hériter », il lui suffit d'avoir la bonne signature, vérifiée par mypy en mode strict au point d'injection. Les stubs de test s'écrivent en cinq lignes.

**Des dataclasses pures dans le domaine, pas pydantic.** La validation appartient aux frontières (config, réponses HTTP) ; le cœur manipule des données déjà validées. Cela garde le domaine sans dépendance et rend l'immuabilité (`frozen=True`) explicite.

**L'incrément d'itération vit dans le nœud review, jamais dans le routeur.** C'est la correction du bug historique : LangGraph ne persiste que les mises à jour d'état retournées par les nœuds ; une mutation dans une fonction de routage conditionnel est silencieusement perdue. Règle du projet : les routeurs sont des fonctions pures de lecture.

**La revue approuve automatiquement si son JSON est illisible.** Un reviewer qui répond hors format ne doit pas bloquer le pipeline en boucle : on logue, on approuve, on publie. C'est un choix de disponibilité plutôt que de perfection.

**Tavily échoue en silence (dégradation, pas panne).** Clé absente ou erreur réseau → contexte de recherche vide, le pipeline continue sur les connaissances du modèle. Un post légèrement moins actuel vaut mieux qu'aucun post.

## Compromis assumés

- **Plus de fichiers, plus d'indirection.** Pour un script de 400 lignes, quatre couches, c'est cher. Le pari : ce projet va grandir (nouvelles sources, nouvelle persistance, peut-être une API), et chaque ajout se paie maintenant en un adapter isolé au lieu d'une chirurgie du cœur.
- **Les prompts vivent dans les adapters.** On pourrait les considérer comme du métier ; ils sont traités comme un détail du fournisseur LLM (ils sont écrits pour des modèles Claude via OpenRouter). Changer de fournisseur peut demander de les réécrire — c'est accepté.
- **Pas de port « horloge » ni d'injection du temps.** `datetime.now()` est appelé directement ; les tests n'ont pas eu besoin de le contrôler. Si un besoin de reproductibilité apparaît, ce sera un port de plus.

## Alternatives envisagées

- **Garder la structure plate en ajoutant juste des tests** : rejeté, le couplage aux clients HTTP rendait les mocks fragiles (patcher des modules entiers plutôt qu'injecter des interfaces).
- **Un port unique « LLM » au lieu de trois ports d'agents** : rejeté, les trois agents ont des contrats métier différents (la revue renvoie un verdict structuré, pas du texte) ; un port générique aurait remonté du parsing JSON dans le use case.

## Voir aussi

- [Référence technique](reference.md) — les signatures exactes des ports et modèles
- [How-to : ajouter un adapter](howto-ajouter-un-adapter.md) — mettre cette architecture à profit
