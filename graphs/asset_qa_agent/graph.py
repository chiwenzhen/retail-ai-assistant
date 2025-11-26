# coding=utf-8
from datetime import UTC, datetime
from typing import Literal, cast

from langchain_core.messages import AIMessage
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode
from langgraph.runtime import Runtime
from langchain.chat_models import init_chat_model
from langchain.tools import tool
from langchain.messages import ToolMessage
from typing import Literal
from langgraph.graph import StateGraph, START, END

from asset_qa_agent.context import Context
from asset_qa_agent.state import InputState, State
from asset_qa_agent.utils import load_chat_model
from asset_qa_agent.tools import database_search


# tools = [database_search]
tools = []
tools_by_name = {tool.name: tool for tool in tools}
model = init_chat_model(
    "qwen3-max",
    model_provider="openai",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    api_key="sk-72fb5cc108ef4c52b08c549d25963bff"
)
model_with_tools = model.bind_tools(tools)

def llm_call(
    state: State, runtime: Runtime[Context]
) -> dict[str, list[AIMessage]]:

    system_message = runtime.context.system_prompt.format(
        system_time=datetime.now(tz=UTC).isoformat()
    )

    return {
        "messages": [
            model_with_tools.invoke(state["messages"])
        ],
        "llm_calls": state.get('llm_calls', 0) + 1
    }

def tool_node(state: dict):
    """Performs the tool call"""

    result = []
    for tool_call in state["messages"][-1].tool_calls:
        tool = tools_by_name[tool_call["name"]]
        observation = tool.invoke(tool_call["args"])
        result.append(ToolMessage(content=observation, tool_call_id=tool_call["id"]))
    return {"messages": result}

def should_continue(state: State) -> Literal["tool_node", END]:
    """Decide if we should continue the loop or stop based upon whether the LLM made a tool call"""

    messages = state["messages"]
    last_message = messages[-1]

    # If the LLM makes a tool call, then perform an action
    if last_message.tool_calls:
        return "tool_node"

    # Otherwise, we stop (reply to the user)
    return END

# 6. Build and compile the agent
# Build workflow
agent_builder = StateGraph(State, input_schema=InputState, context_schema=Context)

# Add nodes
agent_builder.add_node("llm_call", llm_call)
agent_builder.add_node("tool_node", tool_node)

# Add edges to connect nodes
agent_builder.add_edge(START, "llm_call")
agent_builder.add_conditional_edges(
    "llm_call",
    should_continue,
    ["tool_node", END]
)
agent_builder.add_edge("tool_node", "llm_call")

# Compile the agent
graph = agent_builder.compile(name="Asset Qa Agent")


