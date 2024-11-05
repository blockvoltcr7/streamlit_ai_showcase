from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool
import os

# Initialize tools
search_tool = SerperDevTool()

# Create agents
researcher = Agent(
    role='Research Analyst',
    goal='Find the latest trends and developments in Instagram marketing',
    backstory="""You are an expert digital marketing researcher who specializes 
    in social media trends and best practices.""",
    tools=[search_tool],
    verbose=True
)

writer = Agent(
    role='Content Writer',
    goal='Create engaging social media content based on research',
    backstory="""You are a skilled social media copywriter who excels at creating 
    viral Instagram posts that drive engagement.""",
    verbose=True
)

# Define tasks
research_task = Task(
    description="""Research the top 3 current Instagram marketing trends for small businesses.
    Focus on engagement rates, best posting times, and content types that perform well.""",
    agent=researcher,
    expected_output="A detailed report on the top 3 Instagram marketing trends with supporting data"
)

writing_task = Task(
    description="""Using the research provided, create 3 Instagram post ideas
    that follow current best practices. Include captions and hashtag suggestions.
    Previous task output: {previous_task_output}""",
    agent=writer,
    expected_output="3 complete Instagram posts with captions and hashtag suggestions"
)

# Create the crew
crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, writing_task],
    verbose=2,
    process=Process.sequential  # Using sequential process for simple workflow
)

def main():
    # Kick off the crew
    result = crew.kickoff()
    
    # Print the results
    print("\n=== Final Results ===")
    print(result)

if __name__ == "__main__":
    main()