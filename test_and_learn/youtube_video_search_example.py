from crewai import Agent, Task, Crew, Process
from crewai_tools import YoutubeVideoSearchTool

# Initialize the YoutubeVideoSearchTool
youtube_tool = YoutubeVideoSearchTool()

# Create an agent that uses the YoutubeVideoSearchTool
researcher = Agent(
    role='Researcher',
    goal='Find relevant YouTube videos on specific topics',
    backstory='You are an expert researcher specializing in finding relevant YouTube content.',
    tools=[youtube_tool],
    verbose=True
)

# Create a task for the agent
research_task = Task(
    description='Find the top 3 most viewed YouTube videos about artificial intelligence in the last year',
    agent=researcher
)

# Create a crew with the researcher agent
crew = Crew(
    agents=[researcher],
    tasks=[research_task],
    verbose=2,
    process=Process.sequential
)

# Run the crew
result = crew.kickoff()

print(result)
