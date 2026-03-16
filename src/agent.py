import json
import time
from typing import Any, Callable
from langchain.agents import create_agent
from langchain.messages import HumanMessage, RemoveMessage, SystemMessage, ToolMessage
from langgraph.graph.message import REMOVE_ALL_MESSAGES
from android import AndroidDevice
from mobile_tools import build_phone_tools
from langchain.agents.middleware import (
    AgentState,
    ToolCallRequest,
    before_model,
    wrap_tool_call,
)
from langgraph.runtime import Runtime
from langgraph.types import Command

from ui_dict_processing import process_ui_dict
from utils import img_to_base64


class PhoneAgentState(AgentState):
    goal: str
    tools: list[str]


@wrap_tool_call
def remember_tool_invocations(
    request: ToolCallRequest,
    handler: Callable[[ToolCallRequest], ToolMessage | Command],
) -> ToolMessage | Command:
    print(f"Executing tool: {request.tool_call['name']}")
    print(f"Arguments: {request.tool_call['args']}")

    result = handler(request)
    if isinstance(result, ToolMessage):
        request.state["tools"].append(
            f"{request.tool_call['name']} {request.tool_call['args']}, result: {result.content}"
        )
    return result


def build_create_custom_instructions(device: AndroidDevice):
    @before_model(state_schema=PhoneAgentState)
    def create_custom_instructions(state: PhoneAgentState, runtime: Runtime) -> dict[str, Any] | None:
        goal = state.get("goal", "")
        ui_dump = process_ui_dict(device.dump_ui()["hierarchy"])
        ui_text = json.dumps(ui_dump, ensure_ascii=False, indent=2)
        synthetic_messages = [
            SystemMessage(
                content=(
                    "Jesteś agentem sterującym Androidem. "
                    "Jeśli potrzebujesz interakcji z urządzeniem, użyj dostępnych narzędzi."
                )
            ),
            HumanMessage(
                content=[
                    {
                        "type": "text",
                        "text": f"Cel użytkownika:\n{goal}\n\n Wybierz kolejną akcję na podstawie wyłącznie powyższego stanu.",
                    },
                    {
                        "type": "text",
                        "text": f"Historia twoich akcji: \n\n {'\n'.join(state.get("tools", []))}",
                    },
                ]
            ),
        ]

        time.sleep(1)
        screen_bytes = device.screenshot()
        if screen_bytes is not None:
            synthetic_messages.append(
                HumanMessage(
                    content=[
                        {"type": "text", "text": ui_text},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{img_to_base64(screen_bytes)}"},
                        },
                    ],
                ),
            )

        return {
            "messages": [
                RemoveMessage(id=REMOVE_ALL_MESSAGES),
                *synthetic_messages,
            ]
        }

    return create_custom_instructions


def build_agent(llm, device):
    return create_agent(
        model=llm,
        tools=build_phone_tools(device),
        state_schema=PhoneAgentState,
        middleware=[build_create_custom_instructions(device), remember_tool_invocations],  # type: ignore
    )
