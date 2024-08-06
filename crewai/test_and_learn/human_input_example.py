import os
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool
from dotenv import load_dotenv

# Set environment variables for API keys
# Load environment variables from .env file
load_dotenv()

# Set environment variables for API keys
os.environ["SERPER_API_KEY"] = os.getenv("SERPER_API_KEY")
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# Initialize tools
search_tool = SerperDevTool()

# Define agents
researcher = Agent(
    role='AI Research Analyst',
    goal='Conduct thorough research on AI advancements',
    backstory="You're a leading AI researcher with a keen eye for groundbreaking developments.",
    verbose=True,
    allow_delegation=False,
    tools=[search_tool]
)

writer = Agent(
    role='Tech Writer',
    goal='Create engaging content about AI advancements',
    backstory="You're a skilled writer who can explain complex AI concepts to a broad audience.",
    verbose=True,
    allow_delegation=True,
    tools=[search_tool]
)

# Define tasks
research_task = Task(
    description=(
        "Research the latest advancements in AI for the year 2024. "
        "Focus on breakthroughs in natural language processing, computer vision, and robotics. "
        "Compile your findings in a brief report. "
        "Before finalizing, ask the human for any additional areas they'd like you to explore."
    ),
    agent=researcher,
    expected_output="A concise report on AI advancements in 2024",
    human_input=True
)

writing_task = Task(
    description=(
        "Using the researcher's report, write an engaging blog post about AI advancements in 2024. "
        "The post should be informative yet accessible to a general tech-savvy audience. "
        "Before publishing, ask the human to review and suggest any improvements."
    ),
    agent=writer,
    expected_output="An engaging blog post about AI advancements in 2024",
    human_input=True
)

# Create the crew
ai_research_crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, writing_task],
    verbose=2,
    process=Process.sequential
)

# Execute the crew's tasks
result = ai_research_crew.kickoff()

print("\n=== Final Output ===")
print(result)