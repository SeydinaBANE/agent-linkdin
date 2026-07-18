# How to : configurer l'agent

Comment régler les clés API, les modèles, la boucle de réécriture et les chemins de sortie, sans toucher au code.

## Prérequis

- Le projet installé (`uv sync`)
- Un fichier `.env` à la racine (copié depuis `.env_exemple`)

Toute la configuration passe par pydantic-settings (`src/agent_linkdin/config.py`) : chaque champ de `Settings` est surchargeable par une variable d'environnement du même nom en majuscules, dans `.env` ou dans l'environnement du shell.

## Changer de modèle LLM

Les trois agents peuvent utiliser des modèles différents. Les noms utilisent le préfixe `anthropic/` car les appels passent par OpenRouter :

```bash
# .env
RESEARCH_MODEL=anthropic/claude-haiku-4-5
DRAFT_MODEL=anthropic/claude-sonnet-5
REVIEW_MODEL=anthropic/claude-opus-4-8
```

Vérification : lance `uv run agent-linkdin "test" --verbose` et observe le modèle dans les logs d'appel.

## Autoriser plus (ou moins) de réécritures

```bash
# .env
MAX_ITERATIONS=3
```

`MAX_ITERATIONS` compte les réécritures après rejet, pas les brouillons : avec la valeur 3, l'agent produit au maximum 4 brouillons (l'initial + 3 réécritures). À `0`, le premier brouillon est publié quel que soit le verdict de la revue.

## Régler la recherche web

```bash
# .env
TAVILY_API_KEY=tvly-dev-...
SEARCH_MAX_RESULTS=8
SEARCH_TIMEOUT_S=20
```

Sans `TAVILY_API_KEY`, la recherche est désactivée proprement : l'agent Research reçoit un contexte vide et s'appuie sur les connaissances du modèle. Une erreur réseau Tavily ne fait jamais échouer le pipeline — elle est loguée et le pipeline continue sans résultats web.

## Changer le dossier de sortie

```bash
# .env
OUTPUT_DIR=/chemin/vers/mes/posts
```

Les sous-dossiers `posts/` et `traces/` sont créés automatiquement.

## Vérification

```bash
uv run agent-linkdin "sujet de test" --verbose
```

Les logs affichent chaque étape ; le récapitulatif final donne les chemins exacts des fichiers écrits.

## Dépannage

| Symptôme | Cause | Correction |
|---|---|---|
| `OPENROUTER_API_KEY manquante — renseigne-la dans .env` (code retour 1) | `.env` absent ou clé vide | `cp .env_exemple .env` puis renseigner la clé |
| `TAVILY_API_KEY absente — recherche web désactivée` dans les logs | Clé Tavily non renseignée | Normal si voulu ; sinon ajouter la clé dans `.env` |
| `Erreur Tavily : ...` dans les logs | Timeout ou clé invalide | Augmenter `SEARCH_TIMEOUT_S` ou vérifier la clé ; le pipeline continue quand même |
| `Réponse review illisible (...) — approbation automatique` | Le reviewer n'a pas renvoyé du JSON valide | Comportement de sécurité voulu (pas de boucle infinie) ; réessayer ou changer `REVIEW_MODEL` |

## Voir aussi

- [Référence technique](reference.md) — la liste exhaustive des variables avec types et défauts
- [Explication : l'architecture hexagonale](explication-architecture.md) — pourquoi la config est centralisée dans la composition root
