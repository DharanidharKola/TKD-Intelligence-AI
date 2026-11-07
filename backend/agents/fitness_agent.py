from backend.llm import get_llm
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


def answer_fitness_question(question: str, chat_history=None, user_level="Beginner"):
    chat_history = chat_history or []
    history = format_chat_history(chat_history)
    retrieval_query = f"Recent conversation:\\n{history}\\nCurrent question: {question}"[-1800:]
    terminology_context = format_terminology_context(retrieval_query)
    llm = get_llm()

    prompt = f"""
You are an expert Taekwondo Strength and Conditioning Assistant.

Help athletes improve strength, stamina, endurance, flexibility, mobility,
explosive power and recovery.

Instructions:
- Give practical Taekwondo-specific exercises in simple steps.
- Include sets, repetitions, duration and rest periods where appropriate.
- Include warm-up and cool-down recommendations.
- Adjust difficulty to the user's experience level.
- Avoid excessive volume; recommend gradual progression.
- Never encourage training through pain or injury.
- Do not diagnose medical conditions. Recommend a qualified healthcare
  professional for injuries or persistent pain.
- Use recent conversation to understand follow-ups such as "make it easier",
  "add more stamina work" or "turn that into a weekly plan".
- Do not repeat the previous answer unless asked.

Experience level: {user_level}

Recent conversation:
{history}

Current user question:
{question}

Terminology reference:
{terminology_context}

Use the terminology reference when relevant. Preserve reference spellings,
do not invent unsupported definitions, and do not expose internal PDF names,
page numbers or citations.
"""
    response = llm.invoke(prompt)
    return {"answer": response.content, "sources": []}


if __name__ == "__main__":
    q = "Create a weekly fitness plan to improve stamina and explosive power."
    print(answer_fitness_question(q)["answer"])
