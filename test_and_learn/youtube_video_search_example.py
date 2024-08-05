from crewai import Agent, Task, Crew, Process
from crewai_tools import YoutubeVideoSearchTool

def main():
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

    # Get user input for the search query
    search_query = input("Enter a topic to search for YouTube videos: ")
    time_frame = input("Enter the time frame (e.g., 'last year', 'last month', 'all time'): ")

    # Create a task for the agent
    research_task = Task(
        description=f'Find the top 3 most viewed YouTube videos about {search_query} in the {time_frame}',
        agent=researcher
    )

    # Create a crew with the researcher agent
    crew = Crew(
        agents=[researcher],
        tasks=[research_task],
        verbose=2,
        process=Process.sequential
    )

    try:
        # Run the crew
        result = crew.kickoff()
        print("\nSearch Results:")
        print(result)
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
