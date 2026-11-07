from backend.llm import get_llm
from backend.rag.retriever import retrieve_rules
from backend.rag.terminology_retriever import format_terminology_context


def format_chat_history(chat_history):
    if not chat_history:
        return "No previous conversation."
    lines = []
    for item in chat_history[-6:]:
        role = item.get("role", "")
        content = str(item.get("content", "")).strip()
        if role in ("user", "assistant") and content:
            label = "User" if role == "user" else "Assistant"
            lines.append(f"{label}: {content[:1000]}")
    return "\\n".join(lines) if lines else "No previous conversation."


def answer_rules_question(question: str, chat_history=None, user_level="Beginner"):
    chat_history = chat_history or []
    history = format_chat_history(chat_history)

    # Recent context helps resolve short follow-up questions during retrieval.
    retrieval_query = f"Recent conversation:\\n{history}\\nCurrent question: {question}"[-1800:]
    rules = retrieve_rules(retrieval_query, k=3)
    terminology_context = format_terminology_context(question, k=2)

    if not rules:
        return {
            "answer": "I couldn't find relevant information in the WT Rules document.",
            "sources": []
        }

    context_parts, sources = [], []
    for rule in rules:
        page = rule.get("page")
        content = rule.get("content", "")[:1800]
        context_parts.append(
            f"Source: {rule.get('source')}\\nPDF Page: {page}\\nRule Content:\\n{content}"
        )
        sources.append({"source": rule.get("source"), "page": page})

    context = "\\n\\n".join(context_parts)
    prompt = f"""
You are the World Taekwondo Rules Assistant.

Answer official rules questions using ONLY the retrieved WT Competition Rules
and Interpretation passages below.

Rules:
1. Never guess or invent rules, penalties, article numbers or referee decisions.
2. Use article numbers and PDF pages internally only; never display them.
3. Do not expose document names, filenames, page numbers or citations.
4. If retrieved passages are insufficient, say so clearly. Never guess.
5. Preserve the actual meaning of the official rules.
6. Conversation history is only for understanding follow-up references. It is
   NOT an official rules source.
7. Keep the answer clear and professional.

Experience level: {user_level}

Recent conversation:
{history}

Retrieved WT rules:
{context}

Supplementary terminology:
{terminology_context}

Terminology is not an official source for WT regulations, scoring, penalties
or referee decisions.

Current user question:
{question}

Resolve references such as "what about then?" using the conversation, but
verify every official rules claim using only the retrieved WT passages.
"""
    response = get_llm().invoke(prompt)
    return {"answer": response.content, "sources": sources}


if __name__ == "__main__":
    q = "What happens if a contestant intentionally attacks a fallen opponent?"
    print(answer_rules_question(q)["answer"])
