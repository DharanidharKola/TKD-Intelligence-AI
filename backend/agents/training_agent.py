from backend.llm import get_llm
from backend.rag.terminology_retriever import format_terminology_context
from backend.response_cleaner import clean_ai_response


def format_chat_history(chat_history):
    """Format recent turns as readable, newline-separated conversation history."""
    if not chat_history:
        return "No previous conversation."

    lines = []
    for item in chat_history[-6:]:
        role = item.get("role", "")
        content = str(item.get("content", "")).strip()
        if role in ("user", "assistant") and content:
            label = "User" if role == "user" else "Assistant"
            lines.append(f"{label}: {content[:1000]}")

    return "\n".join(lines) if lines else "No previous conversation."


def answer_training_question(question: str, chat_history=None, user_level="Beginner"):
    chat_history = chat_history or []
    history = format_chat_history(chat_history)

    # Keep the retrieval query readable and focused on the current question.
    retrieval_query = (
        f"Recent conversation:\n{history}\nCurrent question: {question}"
    )[-1800:]
    terminology_context = format_terminology_context(retrieval_query)

    llm = get_llm()

    
    prompt = f"""
You are TKD Intelligence's Taekwondo Training Assistant.

Help students improve techniques, kicking skills, combinations, balance
and overall Taekwondo performance.

RESPONSIBILITIES:
- Explain techniques step by step.
- Recommend practical drills and combinations.
- Explain body positioning, balance and common mistakes.
- Suggest corrections and useful coaching cues.
- Create daily and weekly training plans.
- Include sets, repetitions and rest periods where appropriate.
- Adapt difficulty to experience level.
- Never recommend training through pain or injury.

RESPONSE FORMAT:
- Answer the question directly.
- Use clear, short headings where useful.
- Use bullet points for recommendations and examples.
- Use numbered lists for ordered instructions.
- Avoid tables unless explicitly requested.
- Keep paragraphs short.
- Avoid repeated phrases, words and explanations.
- Use natural English.
- Include Korean terminology only when relevant.

TRAINING PLANS:
- Cover every requested day.
- Keep each day's activities concise and practical.
- Include warm-up, main drills and cool-down where appropriate.
- Balance training intensity and recovery.
- Never leave a plan incomplete.

CONVERSATION:
Use recent conversation to understand follow-ups and modifications.
Do not repeat previous answers unnecessarily.

Experience: {user_level}

Recent conversation:
{history}

Question:
{question}

Terminology:
{terminology_context}

Preserve terminology spellings. Do not invent unsupported definitions.
Never expose internal PDF references or citations.
"""


    response = llm.invoke(prompt)

    clean_answer = clean_ai_response(response.content)

    return {
        "answer": clean_answer,
        "sources": []
    }


if __name__ == "__main__":
    q = "Give me five drills to improve my roundhouse kick (Dollyo Chagi)."
    print(answer_training_question(q)["answer"])
