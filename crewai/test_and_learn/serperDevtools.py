"""
This script uses CrewAI to research how QA engineers can transition to AI test engineers.
It employs two agents: a Researcher and an Analyst, working sequentially to gather and analyze information.
"""

import os
import tiktoken
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool, BaseTool
from langchain_openai import ChatOpenAI
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult


class TokenCounterCallback(BaseCallbackHandler):
    """
    Callback handler to count tokens used in LLM calls.
    """

    def __init__(self):
        self.token_count = 0
        self.encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")

    def on_llm_start(self, serialized, prompts, **kwargs):
        """Count tokens in the prompt."""
        for prompt in prompts:
            self.token_count += len(self.encoding.encode(prompt))

    def on_llm_end(self, response: LLMResult, **kwargs):
        """Count tokens in the LLM response."""
        for generation in response.generations:
            for output in generation:
                self.token_count += len(self.encoding.encode(output.text))


class FileWriterTool(BaseTool):
    """
    Tool for writing agent outputs to files.
    """
    name: str = "File Writer"
    description: str = "Writes the agent's output to a file"

    def _run(self, output: str, agent_name: str) -> str:
        """
        Write the given output to a file named after the agent.

        Args:
            output (str): The content to write to the file.
            agent_name (str): The name of the agent, used for the filename.

        Returns:
            str: A message confirming where the output was written.
        """
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

# Define the Researcher agent
researcher = Agent(
    role='Researcher',
    goal='Find the most relevant and up-to-date information on the given topic. Write the results to the file',
    backstory='You are an expert researcher with a knack for finding accurate information quickly.',
    tools=[search_tool, file_writer],
    verbose=True,
    llm=gpt_3_5_turbo
)

# Define the Analyst agent
analyst = Agent(
    role='Analyst',
    goal='Analyze and summarize the information provided by the Researcher. Write the results to the file',
    backstory='You are a skilled analyst with a talent for synthesizing complex information into clear insights.',
    tools=[file_writer],
    verbose=True,
    llm=gpt_3_5_turbo
)

# Define the research task
research_task = Task(
    description='Search the latest trends on how QA engineers can become AI test engineers',
    agent=researcher,
    expected_output="A comprehensive list of articles, blogs, and resources on how QA engineers can transition to AI test engineers."
)

# Define the analysis task
analysis_task = Task(
    description='Analyze and summarize the research findings',
    agent=analyst,
    expected_output="A detailed summary of the research findings, highlighting key insights and recommendations."
)

# Create the crew
crew = Crew(
    agents=[researcher, analyst],
    tasks=[research_task, analysis_task],
    verbose=2,
    process=Process.sequential
)

# Execute the crew's tasks
result = crew.kickoff()

# Write the final result to a file
final_result_str = str(result)  # Convert CrewOutput to string
file_writer.run(final_result_str, "Final_Result")

# Print results and statistics
print("Final Result:")
print(final_result_str)

print(f"\nTotal tokens used: {token_counter.token_count}")

print("\nIndividual agent outputs have been saved to separate files:")
print("- Researcher_output.txt")
print("- Analyst_output.txt")
print("- Final_Result.txt")