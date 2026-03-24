"""
Agent immobilier LangGraph avec outils.
"""

import os
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

from src.tools import all_tools

MODEL = "claude-sonnet-4-5-20250929"

SYSTEM_PROMPT = """
Tu es ImmoBot, un expert immobilier intelligent spécialisé sur le marché d'Île-de-France.
Tu assistes les utilisateurs dans leur recherche de biens immobiliers, leurs questions sur la fiscalité,
la réglementation, les diagnostics, les étapes d'un achat ou d'une location, et tout sujet lié à l'immobilier.

Tu disposes de 4 outils :
- recherche_rag : pour chercher dans la base documentaire (guides, réglementation, infos agence, descriptions de biens)
- recherche_filtree : pour rechercher des biens par critères exacts (ville, prix, surface, pièces, DPE, équipements)
- calcul_frais_notaire : pour calculer précisément les frais de notaire
- simulation_pret : pour simuler un prêt immobilier (mensualités, coût total, taux d'endettement)

Règles :
- Réponds toujours en français.
- Utilise les outils quand c'est pertinent. Ne devine pas les chiffres, utilise les outils de calcul.
- Pour une recherche de biens avec critères précis, utilise recherche_filtree plutôt que recherche_rag.
- Pour les questions sur la réglementation, la fiscalité ou les guides, utilise recherche_rag.
- Quand tu présentes des biens, mentionne les informations clés : prix, surface, ville, nombre de pièces, DPE, équipements.
- Sois professionnel, chaleureux et pédagogue.
- Si tu ne connais pas la réponse, dis-le clairement.
"""
api_key = "sk-vgDIzA7zsqnIg5vFHIahnQ"

# llm = ChatAnthropic(
#     temperature=0,
#     model=MODEL,
#     anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
# )
llm = ChatOpenAI(
    model_name="gpt-4o-mini", 
    base_url="https://ai-gateway.liora.tech/",
    temperature=0,
    api_key=api_key)

agent = create_agent(
    model=llm,
    tools=all_tools,
    system_prompt=SYSTEM_PROMPT,
)


def answer_question(question: str, history: list[dict] = []) -> str:
    """
    Envoie une question à l'agent et retourne la réponse.
    """
    messages = []
    for m in history:
        content = m["content"]
        if isinstance(content, list):
            content = " ".join(
                part.get("text", "") if isinstance(part, dict) else str(part)
                for part in content
            )
        messages.append({"role": m["role"], "content": str(content)})
    messages.append({"role": "user", "content": question})

    result = agent.invoke({"messages": messages})

    # Extraire les outils utilisés
    tools_used = []
    for msg in result["messages"]:
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            for tc in msg.tool_calls:
                tools_used.append(tc["name"])

    ai_message = result["messages"][-1]
    answer = ai_message.content

    if tools_used:
        from collections import Counter
        counts = Counter(tools_used)
        parts = []
        for tool_name, count in counts.items():
            if count > 1:
                parts.append(f"`{tool_name}` (x{count})")
            else:
                parts.append(f"`{tool_name}`")
        answer += f"\n\n---\n*Outils utilisés : {', '.join(parts)}*"

    return answer
