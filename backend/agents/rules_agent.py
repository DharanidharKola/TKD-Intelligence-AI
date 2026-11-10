
from backend.llm import get_llm
from backend.rag.retriever import retrieve_rules
from backend.rag.terminology_retriever import format_terminology_context


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
You are the World Taekwondo Rules Assistant.

Answer using ONLY the retrieved WT Competition Rules passages
for official rules, penalties, scoring and referee decisions.

IMPORTANT RULES:
1. Never invent rules, penalties or article numbers.
2. Do not display PDF filenames or page numbers.
3. If the retrieved passages are insufficient, say so clearly.
4. Preserve the actual meaning of the official rules.
5. Use conversation history only to understand follow-up questions.
6. Terminology is supplementary and is not an official rules source.
7. Give a clear, concise and professional answer.
8. Prefer bullet points when explaining multiple scenarios.

Experience level: {user_level}

Recent conversation:
{history}

Retrieved WT rules:
{context}

Supplementary terminology:
{terminology_context}

Current user question:
{question}

Resolve references using conversation history, but verify every
official rules claim using only the retrieved WT rules.
"""

    response = get_llm().invoke(prompt)

    return {
        "answer": response.content,
        "sources": sources,
    }


if __name__ == "__main__":
    question = (
        "What happens if a contestant intentionally "
        "attacks a fallen opponent?"
    )

    result = answer_rules_question(question)
    print(result["answer"])
