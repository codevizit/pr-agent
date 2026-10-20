from langgraph.graph import END, START, StateGraph

from agent.graphs.state import ReviewState
from agent.nodes.fetch_diff import fetch_diff
from agent.nodes.filter_chunk import filter_chunk
from agent.nodes.post_comments import post_comments
from agent.nodes.review_chunks import review_chunks


def build_review_graph():
    g = StateGraph(ReviewState)
    g.add_node("fetch_diff", fetch_diff)
    g.add_node("filter_chunk", filter_chunk)
    g.add_node("review_chunks", review_chunks)
    g.add_node("post_comments", post_comments)
    g.add_edge(START, "fetch_diff")
    g.add_edge("fetch_diff", "filter_chunk")
    g.add_edge("filter_chunk", "review_chunks")
    g.add_edge("review_chunks", "post_comments")
    g.add_edge("post_comments", END)
    return g.compile()