
from backend.llm import get_llm
from backend.rag.retriever import retrieve_rules
from backend.rag.terminology_retriever import format_terminology_context
import re
from backend.response_cleaner import clean_ai_response

def clean_ai_response(text: str) -> str:
    """Remove internal PDF references and citation markers."""

    patterns = [
        r"\[\s*PDF\s*[\d.]+\s*\]",
        r"\[\s*PDF\s*Page\s*[\d.]+\s*\]",
        r"\[\s*Page\s*[\d.]+\s*\]",
        r"\[\s*p\.?\s*\d+[\d.]*\s*\]",
        r"【\s*PDF\s*[\d.]+\s*】",
        r"\(\s*PDF\s*[\d.]+\s*\)",
    ]

    for pattern in patterns:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)

    # Clean up excessive spaces and blank lines.
    text = re.sub(r" {2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def format_chat_history(chat_history):
    """Keep only a small amount of recent conversation context."""

    if not chat_history:
        return "No previous conversation."

    lines = []

    for item in chat_history[-2:]:
        role = item.get("role", "")
        content = str(item.get("content", "")).strip()

        if role not in ("user", "assistant") or not content:
            continue

        label = "User" if role == "user" else "Assistant"

        # Use the ending of long responses, which is often more useful
        # for resolving a follow-up question.
        content = content[-350:]

        lines.append(f"{label}: {content}")

    return "\n".join(lines) if lines else "No previous conversation."


def answer_rules_question(
    question: str,
    chat_history=None,
    user_level="Beginner",
):
    chat_history = chat_history or []

    history = format_chat_history(chat_history)

    # Include the current question and concise recent context
    # so follow-up questions can be resolved.
    retrieval_query = f"{history}\nCurrent question: {question}"
    retrieval_query = retrieval_query[-1000:]

    # Retrieve no more than four WT Rules passages.
    rules = retrieve_rules(retrieval_query, k=4)

    if not rules:
        return {
            "answer": (
                "I couldn't find relevant information in the "
                "WT Competition Rules document. Please rephrase "
                "your question or provide more context."
            ),
            "sources": [],
        }

    context_parts = []
    sources = []

    for rule in rules:
        page = rule.get("page")
        content = rule.get("content", "")[:1200]

        context_parts.append(
            f"PDF Page: {page}\n"
            f"Rule Content:\n{content}"
        )

        sources.append({
            "source": rule.get("source"),
            "page": page,
        })

    context = "\n\n".join(context_parts)

    # Keep supplementary terminology small and secondary.
    try:
        terminology_context = (
            format_terminology_context(question, k=1) or ""
        )
        terminology_context = str(terminology_context)[:600]
    except Exception:
        terminology_context = ""

    
    prompt = f"""
You are TKD Intelligence's World Taekwondo Rules Assistant.

Answer questions about official WT Competition Rules, scoring, penalties
and referee decisions.

SOURCE PRIORITY:
- Use ONLY the retrieved WT rules passages for official rule claims.
- Never invent articles, penalties, scoring values or regulations.
- If the retrieved passages are insufficient, clearly say so.
- Preserve the meaning of the official rules.
- Terminology is supplementary and is not an official rules source.
- Never expose PDF names, page numbers, source identifiers or citations.

RESPONSE FORMAT:
- Give the direct answer first.
- Prefer short headings and bullet points.
- Use numbered steps for referee procedures.
- Explain scoring consequences when supported by the retrieved rules.
- Avoid unnecessary repetition.
- Do not use tables unless explicitly requested.
- Keep the answer concise but complete.

CONVERSATION:
Use recent conversation only to understand follow-up questions.
Verify every official rules claim against the retrieved passages.
Do not treat previous assistant answers as official sources.

Experience: {user_level}

Recent conversation:
{history}

Retrieved WT rules:
{context}

Supplementary terminology:
{terminology_context}

Question:
{question}

If the retrieved rules do not establish an answer, state that clearly.
"""


    response = get_llm().invoke(prompt)

    clean_answer = clean_ai_response(response.content)

    return {
        "answer": clean_answer,
        "sources": [],
    }


if __name__ == "__main__":
    question = (
        "What happens if a contestant intentionally "
        "attacks a fallen opponent?"
    )

    result = answer_rules_question(question)
    print(result["answer"])
