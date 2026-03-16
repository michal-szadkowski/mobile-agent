import dotenv
from langchain.messages import AIMessageChunk
from langchain_deepseek import ChatDeepSeek


from agent import build_agent, PhoneAgentState
from android import AndroidDevice

dotenv.load_dotenv()

device = AndroidDevice.connect()

# llm = ChatOpenRouter(
#     model="openai/gpt-5-mini",
# )

llm = ChatDeepSeek(
    model="Qwen3.5-9B",
    api_base="http://localhost:8080/v1",
    extra_body={"chat_template_kwargs": {"enable_thinking": True}},
)


agent = build_agent(llm, device)


message = "otwórz stronę reddit.com"
initial_state: PhoneAgentState = {"messages": [], "goal": message, "tools": []}

for chunk in agent.stream(
    initial_state,  # type: ignore[arg-type]
    stream_mode=["messages"],
    version="v2",
):
    if chunk["type"] == "messages":
        token, metadata = chunk["data"]
        if not isinstance(token, AIMessageChunk):
            continue
        reasoning = [b for b in token.content_blocks if b["type"] == "reasoning"]
        text = [b for b in token.content_blocks if b["type"] == "text"]
        if reasoning:
            print(f"{reasoning[0]['reasoning']}", end="")  # type: ignore
        if text:
            print(text[0]["text"], end="")
