from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END

from backend.llm import get_llm
from backend.agents.rules_agent import answer_rules_question
from backend.agents.training_agent import answer_training_question
from backend.agents.fitness_agent import answer_fitness_question
from backend.agents.competition_agent import answer_competition_question


class TaekwondoState(TypedDict):
    question: str
    category: str
    response: str
    sources: List[Dict[str, Any]]
    chat_history: List[Dict[str, str]]
    user_level: str


def format_chat_history(chat_history):
    if not chat_history:
        return "No previous conversation."
    rows = []
    for item in chat_history[-6:]:
        role, content = item.get("role", ""), str(item.get("content", "")).strip()
        if role in ("user", "assistant") and content:
            rows.append(f"{role.capitalize()}: {content[:1000]}")
    return "\\n".join(rows) if rows else "No previous conversation."


def classify_question(state: TaekwondoState):
    history = format_chat_history(state.get("chat_history", []))
    prompt = f"""
You supervise a Taekwondo AI Assistant. Classify the CURRENT question into
exactly one category: rules, training, fitness, competition.

rules = official WT regulations, scoring, penalties, fouls, referee decisions.
training = terminology, Korean commands, techniques, kicks, stances, blocks,
punches, drills and Poomsae.
fitness = strength, stamina, flexibility, conditioning and recovery.
competition = tournament preparation, match strategy, tactics and opponent analysis.

Use recent conversation to classify short follow-ups:
- Follow-up about drills/techniques -> training.
- Follow-up about a penalty/rule -> rules.
- Follow-up about a workout/conditioning -> fitness.
- Follow-up about tournament tactics/preparation -> competition.

Recent conversation:
{history}

Current question: {state['question']}

Return only the category name.
"""
    result = get_llm().invoke(prompt)
    category = result.content.strip().lower()
    if category not in ["rules", "training", "fitness", "competition"]:
        category = "training"
    print(f"\\nSupervisor selected: {category}")
    return {"category": category}


def route_question(state: TaekwondoState):
    return state["category"]


def rules_agent_node(state: TaekwondoState):
    result = answer_rules_question(
        state["question"], state.get("chat_history", []),
        state.get("user_level", "Beginner")
    )
    return {"response": result["answer"], "sources": result.get("sources", [])}


def training_agent_node(state: TaekwondoState):
    result = answer_training_question(
        state["question"], state.get("chat_history", []),
        state.get("user_level", "Beginner")
    )
    return {"response": result["answer"], "sources": result.get("sources", [])}


def fitness_agent_node(state: TaekwondoState):
    result = answer_fitness_question(
        state["question"], state.get("chat_history", []),
        state.get("user_level", "Beginner")
    )
    return {"response": result["answer"], "sources": result.get("sources", [])}


def competition_agent_node(state: TaekwondoState):
    result = answer_competition_question(
        state["question"], state.get("chat_history", []),
        state.get("user_level", "Beginner")
    )
    return {"response": result["answer"], "sources": result.get("sources", [])}


def create_supervisor():
    workflow = StateGraph(TaekwondoState)
    workflow.add_node("classifier", classify_question)
    workflow.add_node("rules_agent", rules_agent_node)
    workflow.add_node("training_agent", training_agent_node)
    workflow.add_node("fitness_agent", fitness_agent_node)
    workflow.add_node("competition_agent", competition_agent_node)
    workflow.set_entry_point("classifier")
    workflow.add_conditional_edges(
        "classifier", route_question,
        {
            "rules": "rules_agent",
            "training": "training_agent",
            "fitness": "fitness_agent",
            "competition": "competition_agent"
        }
    )
    for node in ("rules_agent", "training_agent", "fitness_agent", "competition_agent"):
        workflow.add_edge(node, END)
    return workflow.compile()


if __name__ == "__main__":
    graph = create_supervisor()
    q = "Give me a 7-day Taekwondo tournament preparation strategy."
    result = graph.invoke({
        "question": q, "category": "", "response": "", "sources": [],
        "chat_history": [], "user_level": "Beginner"
    })
    print(result["response"])
