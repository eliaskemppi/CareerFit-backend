# Imports
from langgraph.graph import StateGraph, START, END

from models import JobMatchState
from nodes import (
    analyze_cv,
    analyze_job,
    extract_requirements,
    match_requirements,
    recommend_project,
)

# Setting up graph
graph = StateGraph(JobMatchState)

graph.add_node("analyze_cv", analyze_cv)
graph.add_node("analyze_job", analyze_job)
graph.add_node("extract_requirements", extract_requirements)
graph.add_node("match_requirements", match_requirements)
graph.add_node("recommend_project", recommend_project)

graph.add_edge(START, "analyze_cv")
graph.add_edge("analyze_cv", "analyze_job")
graph.add_edge("analyze_job", "extract_requirements")
graph.add_edge("extract_requirements", "match_requirements")
graph.add_edge("match_requirements", "recommend_project")
graph.add_edge("recommend_project", END)

graph_app = graph.compile()