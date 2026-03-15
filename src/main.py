import dotenv
from langchain_deepseek import ChatDeepSeek
from langchain_openrouter import ChatOpenRouter

from agent import build_agent, PhoneAgentState
from android import AndroidDevice

dotenv.load_dotenv()

device = AndroidDevice.connect()

llm = ChatOpenRouter(
    model="openai/gpt-5-nano",
)

# llm = ChatDeepSeek(
#     model="Qwen3.5-9B",
#     api_base="http://localhost:8080/v1",
# )


agent = build_agent(llm, device)


message = "otwórz aplikację notatek keep, utwórz nową notatkę, dodaj treść test"

result = agent.invoke(PhoneAgentState(messages=[], goal=message, tools=[]))  # type: ignore

print(result)
