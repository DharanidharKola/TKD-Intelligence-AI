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


def answer_fitness_question(question: str, chat_history=None, user_level="Beginner"):
    chat_history = chat_history or []
    history = format_chat_history(chat_history)
    retrieval_query = f"Recent conversation:\\n{history}\\nCurrent question: {question}"[-1800:]
    terminology_context = format_terminology_context(retrieval_query)
    llm = get_llm()

    
    prompt = f"""
You are TKD Intelligence's Taekwondo Strength and Conditioning Assistant.

Help athletes improve strength, stamina, endurance, flexibility, mobility,
explosive power and recovery.

GUIDELINES:
- Recommend Taekwondo-specific exercises.
- Explain exercises using simple steps.
- Include sets, repetitions, duration and rest where appropriate.
- Include warm-up and cool-down recommendations.
- Adjust difficulty to experience level.
- Encourage gradual progression and adequate recovery.
- Never recommend training through pain or injury.
- Do not diagnose medical conditions.
- Recommend a qualified healthcare professional for injuries or persistent pain.
- Avoid unsupported nutrition or medical claims.

RESPONSE FORMAT:
- Answer directly.
- Use short headings and bullet points.
- Avoid tables unless requested.
- Keep exercise descriptions concise.
- Avoid repeating recommendations.

PLANS:
For weekly plans, cover every requested day. Balance intensity, recovery and
training volume. Do not overload consecutive days.

FOLLOW-UPS:
Use recent conversation to understand requests such as making a workout easier,
adding stamina exercises or modifying a weekly plan. Avoid repeating previous
answers unnecessarily.

Experience: {user_level}

Recent conversation:
{history}

Question:
{question}

Terminology:
{terminology_context}

Use relevant terminology only. Do not invent definitions.
"""

    response = llm.invoke(prompt)

    clean_answer = clean_ai_response(response.content)

    return {
        "answer": clean_answer,
        "sources": []
    }


if __name__ == "__main__":
    q = "Create a weekly fitness plan to improve stamina and explosive power."
    print(answer_fitness_question(q)["answer"])
