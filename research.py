"""
Research Agent — Scans trends and extracts insights
Model: Claude Haiku
Search: Tavily (résultats web réels et récents)
"""

import anthropic
import os
import requests
from dotenv import load_dotenv
load_dotenv()

SYSTEM_PROMPT = """Réponds toujours en français.
Tu es un analyste LinkedIn expert. À partir des résultats de recherche web fournis, tu dois :
1. Identifier les 3-5 angles les plus pertinents et actuels sur le sujet
2. Extraire des faits concrets, stats ou observations qui résonnent avec une audience tech/business
3. Proposer un POV unique ou une prise de position contre-intuitive qui se démarquerait sur LinkedIn
4. Noter ce qui est surutilisé sur ce sujet (pour éviter les clichés)

Sois spécifique. Pas de généralités. Appuie-toi sur les données réelles des résultats de recherche.
Formate ta réponse ainsi :

## Angles clés
[points]

## Faits & Stats concrets
[points tirés des résultats de recherche]

## POV unique
[1-2 phrases]

## Clichés à éviter
[points]

## Sources utilisées
[liste des URLs pertinentes]
"""


def search_web(query: str, max_results: int = 5) -> list:
    """Recherche web via Tavily API."""
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        print("   ⚠️  TAVILY_API_KEY manquante — recherche web désactivée")
        return []

    try:
        response = requests.post(
            "https://api.tavily.com/search",
            json={
                "api_key": api_key,
                "query": query,
                "max_results": max_results,
                "search_depth": "advanced",
                "include_answer": True,
                "include_raw_content": False,
            },
            timeout=15
        )
        response.raise_for_status()
        data = response.json()

        results = []
        if data.get("answer"):
            results.append({"type": "summary", "content": data["answer"]})

        for r in data.get("results", []):
            results.append({
                "type": "article",
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "content": r.get("content", "")[:500],
                "published_date": r.get("published_date", ""),
            })

        print(f"   🌐 {len(data.get('results', []))} résultats trouvés via Tavily")
        return results

    except Exception as e:
        print(f"   ⚠️  Erreur Tavily : {e}")
        return []


def format_search_results(results: list) -> str:
    """Formate les résultats pour le prompt."""
    if not results:
        return "Aucun résultat de recherche disponible. Utilise tes connaissances générales."

    formatted = "=== RÉSULTATS DE RECHERCHE WEB ===\n\n"
    for i, r in enumerate(results, 1):
        if r["type"] == "summary":
            formatted += f"**Résumé :**\n{r['content']}\n\n"
        else:
            formatted += f"**Article {i} :** {r['title']}\n"
            if r.get("published_date"):
                formatted += f"Date : {r['published_date']}\n"
            formatted += f"URL : {r['url']}\n"
            formatted += f"Extrait : {r['content']}\n\n"

    return formatted


def run_research(topic: str) -> str:
    # 1. Recherche web
    print("   🔎 Recherche web en cours...")
    search_results = search_web(f"{topic} 2025 tendances actualité")

    # 2. Analyse avec le LLM
    client = anthropic.Anthropic(
        api_key=os.environ["OPENROUTER_API_KEY"],
        base_url="https://openrouter.ai/api",
    )

    search_context = format_search_results(search_results)

    message = client.messages.create(
        model="anthropic/claude-haiku-4-5",
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"Sujet LinkedIn : **{topic}**\n\n{search_context}\n\nAnalyse ces résultats et produis les insights."
            }
        ]
    )

    return message.content[0].text