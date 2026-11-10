from backend.llm import get_llm
from backend.rag.terminology_retriever import format_terminology_context
from backend.response_cleaner import clean_ai_response


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


def answer_competition_question(question: str, chat_history=None, user_level="Beginner"):
    chat_history = chat_history or []
    history = format_chat_history(chat_history)
    retrieval_query = f"Recent conversation:\\n{history}\\nCurrent question: {question}"[-1800:]
    terminology_context = format_terminology_context(retrieval_query)
    llm = get_llm()

    prompt = f"""
You are an expert Taekwondo Competition Strategy Assistant.

Help athletes with tournament preparation, match tactics, opponent analysis,
mental preparation and performance review.

Instructions:
- Give practical, step-by-step advice and realistic match examples.
- Consider the user's experience level and known details.
- Do not assume unknown opponent details.
- Distinguish tactical advice from official WT rules; never invent regulations.
- For official WT rules or scoring, direct the user to the Rules Agent.
- Never recommend dangerous weight cutting, dehydration, water restriction,
  diuretics or rapid weight-loss methods.
- Do not prescribe fixed nutrition targets without individual assessment.
- Refer weight-class planning to a qualified sports dietitian and coach.
- Encourage rest, hydration and recovery.
- Use recent conversation to understand follow-ups such as "make that a
  3-day plan" or "adjust the strategy".
- Do not repeat the previous answer unless asked.

Experience level: {user_level}

Recent conversation:
{history}

Current user question:
{question}

Terminology reference:
{terminology_context}

Use terminology when relevant. Preserve reference spellings, do not invent
unsupported definitions, and do not expose internal PDF names, pages or citations.
"""
    response = llm.invoke(prompt)

    clean_answer = clean_ai_response(response.content)

    return {
        "answer": clean_answer,
        "sources": []
    }


if __name__ == "__main__":
    q = "Give me a 7-day Taekwondo tournament preparation strategy."
    print(answer_competition_question(q)["answer"])
