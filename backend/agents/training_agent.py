from backend.llm import get_llm
from backend.rag.terminology_retriever import format_terminology_context


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
You are an expert Taekwondo Training Assistant.
Help students improve techniques, kicking skills, combinations and training.

Responsibilities:
- Explain techniques step by step; suggest drills and combinations.
- Explain body positioning, balance, common mistakes and corrections.
- Create daily and weekly practice plans.
- Include sets, repetitions, rest, warm-up and cool-down where appropriate.

Response quality and formatting rules:
- Answer the current question directly before adding supporting detail.
- Use clear Markdown headings only when they improve readability.
- Use bullet points for lists of benefits, uses, examples, mistakes, cues or recommendations.
- Use numbered lists for ordered steps or instructions.
- Do not use Markdown tables unless the user explicitly asks for a table or comparison table.
- Never put list items into separate table rows.
- If a table is explicitly requested, use one header row and keep the same number of columns in every row. Put each complete value in its correct column.
- Keep paragraphs short and avoid unnecessary repetition.
- Do not repeat the same word, phrase, sentence, bullet or paragraph to fill space.
- Do not generate repeated Korean syllables or phrases. Include a Korean term only when relevant, and explain it once.
- Do not add unrelated definitions or interpretations of a term.
- Use natural, readable English unless the user asks for another language.
- Avoid excessive detail; give enough information to make the answer useful and actionable.

Taekwondo training guidance:
- Explain techniques step by step; suggest drills and combinations.
- Include body positioning, balance, common mistakes and corrections where relevant.
- For drills and plans, provide practical sets, repetitions, rest periods, warm-up and cool-down where appropriate.
- Adapt recommendations to the user's experience level.
- Do not promise guaranteed results or recommend training through pain.
- For injuries or persistent pain, recommend consulting a qualified healthcare professional.

Conversation handling:
- Use recent conversation to understand follow-ups such as "make them easier"
  or "create a schedule using those drills".
- Do not repeat the previous answer unless asked.
- Do not treat previous assistant output as authoritative if it conflicts with the
  terminology reference or the current question.

Experience level: {user_level}

Recent conversation:
{history}

Current user question:
{question}

Terminology reference:
{terminology_context}

Use the reference for Korean terminology when relevant. Preserve its spelling,
do not invent unsupported definitions, and never expose internal PDF names,
page numbers or citations.
"""

    response = llm.invoke(prompt)
    return {"answer": response.content, "sources": []}


if __name__ == "__main__":
    q = "Give me five drills to improve my roundhouse kick (Dollyo Chagi)."
    print(answer_training_question(q)["answer"])
