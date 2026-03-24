import os
from pathlib import Path
from langchain_anthropic import ChatAnthropic
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.messages import SystemMessage, HumanMessage, convert_to_messages
from langchain_core.documents import Document

from dotenv import load_dotenv


load_dotenv(override=True)

MODEL = "claude-sonnet-4-5-20250929"
DB_NAME = str(Path(__file__).parent.parent / "vector_db")

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
RETRIEVAL_K = 10

SYSTEM_PROMPT = """
Tu es ImmoBot, un expert immobilier intelligent spécialisé sur le marché d'Île-de-France.
Tu assistes les utilisateurs dans leur recherche de biens immobiliers, leurs questions sur la fiscalité,
la réglementation, les diagnostics, les étapes d'un achat ou d'une location, et tout sujet lié à l'immobilier.

Règles :
- Réponds toujours en français.
- Utilise le contexte fourni pour répondre précisément aux questions.
- Quand tu présentes des biens, mentionne les informations clés : prix, surface, ville, nombre de pièces, DPE, étage, équipements.
- Si on te demande des biens selon des critères (budget, ville, surface...), filtre et présente les résultats de façon structurée.
- Pour les questions juridiques ou fiscales, sois précis et mentionne les conditions et limites.
- Si tu ne connais pas la réponse ou si l'information n'est pas dans le contexte, dis-le clairement.
- Sois professionnel, chaleureux et pédagogue.

Contexte :
{context}
"""

vectorstore = Chroma(persist_directory=DB_NAME, embedding_function=embeddings)
retriever = vectorstore.as_retriever()
llm = ChatAnthropic(temperature=0, model=MODEL, anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"))


def fetch_context(question: str) -> list[Document]:
    """
    Retrieve relevant context documents for a question.
    """
    return retriever.invoke(question, k=RETRIEVAL_K)


def combined_question(question: str, history: list[dict] = []) -> str:
    """
    Combine all the user's messages into a single string.
    """
    prior_parts = []
    for m in history:
        if m["role"] == "user":
            content = m["content"]
            if isinstance(content, list):
                content = " ".join(
                    part.get("text", "") if isinstance(part, dict) else str(part)
                    for part in content
                )
            prior_parts.append(str(content))
    return "\n".join(prior_parts) + "\n" + question


def answer_question(question: str, history: list[dict] = []) -> tuple[str, list[Document]]:
    """
    Answer the given question with RAG; return the answer and the context documents.
    """
    combined = combined_question(question, history)
    docs = fetch_context(combined)
    context = "\n\n".join(doc.page_content for doc in docs)
    system_prompt = SYSTEM_PROMPT.format(context=context)
    messages = [SystemMessage(content=system_prompt)]
    messages.extend(convert_to_messages(history))
    messages.append(HumanMessage(content=question))
    response = llm.invoke(messages)
    return response.content, docs
