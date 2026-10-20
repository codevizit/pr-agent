from typing import TypedDict

from dotenv import load_dotenv

load_dotenv()

from langgraph.graph import END, START, StateGraph

from agent.clients.llm import ask_json


class State(TypedDict, total=False):
    code: str
    review: dict


def review_node(state: State) -> State:
    out = ask_json(
        "You are a code reviewer.",
        'Return {"severity": str, "comment": str} for: ' + state["code"],
    )
    return {"review": out["data"]}


g = StateGraph(State)
g.add_node("reviewer", review_node)
g.add_edge(START, "reviewer")
g.add_edge("reviewer", END)
app = g.compile()

print(app.invoke({"code": "password = 'admin123'"}))