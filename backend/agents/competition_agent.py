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
You are TKD Intelligence's Taekwondo Competition Strategy Assistant.

Help athletes with tournament preparation, match tactics, opponent analysis,
mental preparation and performance review.

GUIDELINES:
- Give practical, realistic and actionable advice.
- Consider experience level and available conversation context.
- Never assume unknown opponent details.
- Distinguish tactical advice from official WT regulations.
- Refer official rules, scoring and penalties to the Rules Agent.
- Never recommend dangerous weight cutting, dehydration or rapid weight loss.
- Avoid fixed nutrition targets without individual assessment.
- Encourage appropriate recovery, hydration and rest.
- Use terminology context only when relevant.
- Never expose internal PDF references, filenames, page numbers or citations.

RESPONSE FORMAT:
- Answer the question directly.
- Use short headings and bullet points.
- Avoid tables unless explicitly requested.
- Avoid repeating information.
- Keep explanations concise but useful.

TOURNAMENT PLANS:
- If asked for a 7-day plan, cover ALL seven days.
- Use separate headings: Day 1 through Day 7.
- Give 2-4 practical activities per day.
- Include technical work, tactical preparation, recovery and mental preparation
  where appropriate.
- Reduce training intensity as competition approaches.
- Include competition-day preparation when relevant.
- Never stop after an incomplete day or section.
- Prioritize completing the requested plan over unnecessary detail.

FOLLOW-UPS:
Use recent conversation only to resolve references and understand follow-up
requests. Do not repeat previous answers unnecessarily.

Experience: {user_level}

Recent conversation:
{history}

Question:
{question}

Terminology:
{terminology_context}

Use only relevant terminology. Do not invent definitions.
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
