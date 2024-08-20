import os
import tiktoken
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from crewai_tools import SerperDevTool
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult

class TokenCounterCallback(BaseCallbackHandler):
    def __init__(self):
        self.token_count = 0
        self.encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")

    def on_llm_start(self, serialized, prompts, **kwargs):
        for prompt in prompts:
            self.token_count += len(self.encoding.encode(prompt))

    def on_llm_end(self, response: LLMResult, **kwargs):
        for generation in response.generations:
            for output in generation:
                self.token_count += len(self.encoding.encode(output.text))

# Initialize tools and callbacks
token_counter = TokenCounterCallback()
search_tool = SerperDevTool()

# Initialize the LLM model
gpt_4o_mini = ChatOpenAI(
    model_name="gpt-4o-mini",    # Changed from "gpt-3.5-turbo" to "gpt-4o-mini"
    temperature=0.7,
    callbacks=[token_counter]
)

# Define the Researcher agent
researcher = Agent(
    role='AI Trend Researcher',
    goal='Find the latest trends and developments in AI',
    backstory='You are an expert researcher specializing in AI and emerging technologies.',
    tools=[search_tool],
    verbose=True,
    llm=gpt_4o_mini
)

# Define the Writer agent
writer = Agent(
    role='Tech Writer',
    goal='Create engaging content about AI trends',
    backstory='You are a skilled writer with a talent for explaining complex tech concepts.',
    verbose=True,
    llm=gpt_4o_mini
)

# Define the Manager agent
manager = Agent(
    role='Project Manager',
    goal='Oversee the research and writing process to produce a high-quality report on AI trends',
    backstory='You are an experienced project manager with a background in tech and a keen eye for detail.',
    allow_delegation=True,
    verbose=True,
    llm=gpt_4o_mini
)

# Define the research task
research_task = Task(
    description='Research the top 3 emerging trends in AI for 2024',
    agent=researcher,
    expected_output="A detailed list of the top 3 emerging AI trends for 2024 with brief explanations"
)

# Define the writing task
writing_task = Task(
    description='Write a 500-word summary report on the top 3 AI trends for 2024 based on the research findings',
    agent=writer,
    expected_output="A 500-word summary report on the top 3 AI trends for 2024"
)

# Create the crew with a custom manager
crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, writing_task],
    manager_agent=manager,
    process=Process.hierarchical
)

# Execute the crew's tasks
result = crew.kickoff()

print("Final Result:")
print(result)

print(f"\nTotal tokens used: {token_counter.token_count}")