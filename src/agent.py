import json
import time
from typing import Annotated, TypedDict
from langchain.chat_models import BaseChatModel
from langchain.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START
from langgraph.graph.message import BaseMessage, StateGraph, add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from ui_dict_processing import process_ui_dict
from utils import img_to_base64
from android import AndroidDevice
from mobile_tools import build_phone_tools


class PhoneState(TypedDict):
    goal: str
    ui_dump: str
    screen_b64: str

    messages: Annotated[list[BaseMessage], add_messages]


def create_graph(llm: BaseChatModel, device: AndroidDevice):
    tools = build_phone_tools(device)
    llm_with_tools = llm.bind_tools(tools)

    def observe(state: PhoneState):
        d = device
        time.sleep(1)
        ui_dump = process_ui_dict(d.dump_ui()["hierarchy"])
        ui_text = json.dumps(ui_dump, ensure_ascii=False, indent=2)

        screen_bytes = d.screenshot()
        screen_b64 = f"data:image/jpeg;base64,{img_to_base64(screen_bytes)}" if screen_bytes is not None else None

        return {
            "ui_dump": ui_text,
            "screen_b64": screen_b64,
        }

    def run_model(state: PhoneState):
        prompt = [
            SystemMessage(
                content=(
                    "You are an Android agent. "
                    "You must achieve the user's goal using the available tools. "
                    "If the task is already complete or you do not need a tool, respond normally. "
                    "Do not invent elements that are not visible on the screen. "
                    "Do not stop until you are sure you have finished the task and can confirm it on screenshot or ui hierarchy "
                    "You should act without feedback from the user."
                )
            ),
            *state.get("messages", []),
            HumanMessage(
                content=[
                    {
                        "type": "text",
                        "text": f"User goal: {state.get('goal', '')}\n",
                    },
                    {
                        "type": "text",
                        "text": f"Current ui state is: \n{state.get("ui_dump", "")} \n Which is visible the attached screenshot.",
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": state.get("screen_b64", "")},
                    },
                ]
            ),
        ]
        response = llm_with_tools.invoke(prompt)
        return {"messages": [response]}

    tool_node = ToolNode(build_phone_tools(device))

    builder = StateGraph(PhoneState)

    builder.add_node("observe", observe)
    builder.add_node("run_model", run_model)
    builder.add_node("tools", tool_node)

    builder.add_edge(START, "observe")
    builder.add_edge("observe", "run_model")

    builder.add_conditional_edges(
        "run_model",
        tools_condition,
        {
            "tools": "tools",
            "__end__": END,
        },
    )

    builder.add_edge("tools", "observe")

    return builder.compile()
