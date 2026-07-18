# Tutoriel : ton premier post LinkedIn généré

Tu vas installer le projet, le configurer et générer un vrai post LinkedIn de 150–250 mots, relu et approuvé par un agent de revue. À la fin, tu auras un fichier Markdown prêt à publier et une trace JSON de tout le pipeline.

## Ce qu'il te faut

- Python ≥ 3.11
- [uv](https://docs.astral.sh/uv/) installé (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- Une clé API [OpenRouter](https://openrouter.ai/keys) (obligatoire)
- Une clé API [Tavily](https://tavily.com) (optionnelle — active la recherche web réelle)

## Étape 1 : installer les dépendances

```bash
git clone https://github.com/SeydinaBANE/agent-linkdin.git
cd agent-linkdin
uv sync
```

`uv sync` crée l'environnement virtuel `.venv` et installe le paquet `agent_linkdin` en mode éditable avec toutes ses dépendances.

## Étape 2 : configurer les clés

```bash
cp .env_exemple .env
```

Ouvre `.env` et renseigne ta clé OpenRouter :

```
OPENROUTER_API_KEY=sk-or-v1-...
TAVILY_API_KEY=tvly-dev-...
```

Si tu laisses `TAVILY_API_KEY` vide, l'agent fonctionne quand même — il s'appuie alors sur les connaissances du modèle au lieu de résultats web récents.

## Étape 3 : générer ton premier post

```bash
uv run agent-linkdin "les agents IA en production en 2025"
```

Tu vois le pipeline dérouler dans les logs : recherche web, analyse, rédaction, puis revue. Si le post est rejeté, il est réécrit avec le feedback du reviewer (2 réécritures max par défaut). À la fin s'affiche :

```
=======================================================
  ✨ POST FINAL
=======================================================
<ton post>

  Itérations : 1
  Post : output/posts/20260718_143012_les_agents_ia_en_production_en.md
  Trace : output/traces/20260718_143012_les_agents_ia_en_production_en.json
```

## Étape 4 : inspecter les résultats

```bash
cat output/posts/*.md
cat output/traces/*.json
```

Le fichier `.md` contient le post final prêt à copier-coller sur LinkedIn. La trace JSON détaille chaque étape : durée de la recherche, durée de chaque brouillon, verdict de chaque revue.

Pour voir tout le détail du pipeline pendant l'exécution, relance avec `--verbose`.

## Ce que tu as construit

Tu as un pipeline multi-agents fonctionnel qui recherche, rédige, critique et itère tout seul. Pour aller plus loin :

- Changer de modèle ou augmenter les réécritures → [How-to : configurer l'agent](howto-configuration.md)
- Comprendre le rôle de chaque couche → [Explication : l'architecture hexagonale](explication-architecture.md)
- La liste complète des options → [Référence technique](reference.md)
