import os
from crewai import Agent, Task, Crew, Process
from langchain_groq import ChatGroq
from dotenv import load_dotenv

# Set up the environment variables for Groq API
# Load environment variables from .env file
load_dotenv()

# Set up the environment variable for Groq API key
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

# Initialize the language model with Groq
groq_llm = ChatGroq(
    temperature=0,
    groq_api_key=os.environ["GROQ_API_KEY"],
    model_name="llama3-8b-8192"  # You can change this to other available models like 'mixtral-8x7b-32768' or 'gemma-7b-it'
)

# Define an agent using the Groq LLM
researcher = Agent(
    role="AI Research Specialist",
    goal="Conduct in-depth research on AI advancements",
    backstory="You are an AI expert with a keen interest in the latest developments in artificial intelligence.",
    verbose=True,
    llm=groq_llm
)

# Define a task for the agent
research_task = Task(
    description="Research and summarize the latest advancements in natural language processing over the past year.",
    agent=researcher,
    expected_output="A comprehensive summary of NLP advancements, including key breakthroughs and their potential applications."
)

# Create a crew with the agent and task
crew = Crew(
    agents=[researcher],
    tasks=[research_task],
    verbose=2,
    process=Process.sequential
)

# Execute the crew's task
result = crew.kickoff()

# Print the result
print(result)