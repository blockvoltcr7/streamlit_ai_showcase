from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from crewai_tools import SerperDevTool, BaseTool
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult
import os
import tiktoken

# Token Counter Callback
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

# File Writer Tool
class FileWriterTool(BaseTool):
    name: str = "File Writer"
    description: str = "Writes the agent's output to a file"

    def _run(self, output: str, agent_name: str) -> str:
        directory = "file_output"
        os.makedirs(directory, exist_ok=True)
        filename = os.path.join(directory, f"{agent_name}_output.txt")
        with open(filename, "w") as f:
            f.write(output)
        return f"Output written to {filename}"

# Initialize tools and callbacks
token_counter = TokenCounterCallback()
search_tool = SerperDevTool()
file_writer = FileWriterTool()

# Initialize the LLM model
gpt_3_5_turbo = ChatOpenAI(
    model_name="gpt-3.5-turbo",
    temperature=0.7,
    callbacks=[token_counter]
)

# Define the agents
manager = Agent(
    role='Project Manager',
    goal='Oversee the market research project and ensure high-quality deliverables',
    backstory='An experienced project manager with a track record of successful product launches',
    verbose=True,
    allow_delegation=True,
    tools=[search_tool, file_writer]
)

researcher = Agent(
    role='Market Researcher',
    goal='Gather comprehensive market data on eco-friendly water bottles',
    backstory='A detail-oriented researcher with expertise in consumer trends',
    verbose=True,
    tools=[search_tool]
)

analyst = Agent(
    role='Data Analyst',
    goal='Interpret market data and identify key insights for eco-friendly water bottles',
    backstory='A skilled analyst with a knack for spotting market opportunities',
    verbose=True,
    tools=[search_tool]
)

writer = Agent(
    role='Report Writer',
    goal='Create a compelling and informative market research report on eco-friendly water bottles',
    backstory='A talented writer with experience in creating impactful business reports',
    verbose=True,
    tools=[file_writer]
)

# Define the tasks
research_task = Task(
    description='Conduct thorough market research on eco-friendly water bottles. Focus on current trends, major players, and consumer preferences.',
    agent=researcher,
    expected_output="A comprehensive report on the eco-friendly water bottle market, including current trends, major players, and consumer preferences."
)

analysis_task = Task(
    description='Analyze the gathered market data. Identify key trends, potential market gaps, and consumer insights for eco-friendly water bottles.',
    agent=analyst,
    expected_output="An analysis report highlighting key trends, potential market gaps, and consumer insights for eco-friendly water bottles."
)

writing_task = Task(
    description='Write a comprehensive market research report on eco-friendly water bottles. Include an executive summary, key findings, and recommendations for market entry.',
    agent=writer,
    expected_output="A comprehensive market research report on eco-friendly water bottles, including an executive summary, key findings, and recommendations for market entry."
)

# Create the crew with a hierarchical process
market_research_crew = Crew(
    agents=[manager, researcher, analyst, writer],
    tasks=[research_task, analysis_task, writing_task],
    verbose=True,  # Changed from 2 to True
    process=Process.hierarchical,
    manager_llm=gpt_3_5_turbo
)

# Execute the crew's tasks
result = market_research_crew.kickoff()

# Write the final result to a file
final_result_str = str(result)
file_writer.run(final_result_str, "Final_Result")

# Print results and statistics
print("Final Result:")
print(final_result_str)

print(f"\nTotal tokens used: {token_counter.token_count}")

print("\nIndividual agent outputs have been saved to separate files:")
print("- Researcher_output.txt")
print("- Analyst_output.txt")
print("- Writer_output.txt")
print("- Final_Result.txt")