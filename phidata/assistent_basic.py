from phi.assistant import Assistant
from phi.llm.openai import OpenAIChat
from phi.tools.duckduckgo import DuckDuckGo

assistant = Assistant(
    llm=OpenAIChat(model="gpt-4o-mini", max_tokens=500, temperature=0.3),
    tools=[DuckDuckGo()],
    show_tool_calls=True
)
assistant.print_response("will there be a god of war 6?", markdown=True)
