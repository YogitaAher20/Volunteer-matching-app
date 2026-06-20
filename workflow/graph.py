from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph
from langgraph.constants import START, END
# Import the existing agents
from agents.profile_agent import analyze_profile
from agents.role_agent import recommend_role
from agents.opportunity_agent import suggest_activities

# 1. Define the shared state structure
class AgentState(TypedDict):
    skills: List[str]
    interests: List[str]
    availability: str
    hours: str
    profile: Dict[str, Any]
    recommendation: Dict[str, Any]
    activities: List[str]

# 2. Define Node 1: Profile Agent Node
def profile_node(state: AgentState) -> Dict[str, Any]:
    """
    Wraps the profile analysis agent. 
    Reads raw variables from the state, runs the analysis, and updates 'profile'.
    """
    profile = analyze_profile(
        skills=state["skills"],
        interests=state["interests"],
        availability=state["availability"],
        hours=state["hours"]
    )
    return {"profile": profile}

# 2. Define Node 2: Role Agent Node
def role_node(state: AgentState) -> Dict[str, Any]:
    """
    Wraps the role recommendation agent.
    Reads structured profile from the state, calls match, and updates 'recommendation'.
    """
    recommendation = recommend_role(state["profile"])
    return {"recommendation": recommendation}

# 2. Define Node 3: Opportunity Agent Node
def opportunity_node(state: AgentState) -> Dict[str, Any]:
    """
    Wraps the opportunity agent.
    Reads recommended role from the state, generates tasks, and updates 'activities'.
    """
    recommended_role = state["recommendation"]["role"]
    opps = suggest_activities(recommended_role)
    return {"activities": opps["activities"]}

# 3. Assemble and compile StateGraph
builder = StateGraph(AgentState)

# Add nodes to graph
builder.add_node("profile_agent", profile_node)
builder.add_node("role_agent", role_node)
builder.add_node("opportunity_agent", opportunity_node)

# Set linear edge sequence
builder.add_edge(START, "profile_agent")
builder.add_edge("profile_agent", "role_agent")
builder.add_edge("role_agent", "opportunity_agent")
builder.add_edge("opportunity_agent", END)

# Compile graph into runner
workflow_graph = builder.compile()
