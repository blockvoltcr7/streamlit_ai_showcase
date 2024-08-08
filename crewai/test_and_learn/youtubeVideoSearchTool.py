import uuid
from pathlib import Path
from crewai import Agent, Task, Crew, Process
from crewai_tools import YoutubeVideoSearchTool
from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseLLM

# Get the directory of the current script
current_dir = Path(__file__).resolve().parent

def write_to_file(content: str, directory=current_dir / 'file_output'):
    """Write content to a file with a unique name in the specified directory."""
    unique_filename = f"youtube_search_{uuid.uuid4()}.txt"
    file_path = directory / unique_filename
    directory.mkdir(parents=True, exist_ok=True)  # Ensure the directory exists
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Output written to: {file_path}")
    return file_path

def create_youtube_search_crew(youtube_video_url: str = None, llm: BaseLLM = None):
    """Create and return a Crew for YouTube video search and analysis."""
    youtube_tool = YoutubeVideoSearchTool(youtube_video_url=youtube_video_url)

    researcher = Agent(
        role='Researcher',
        goal='Find and analyze relevant YouTube videos on specific topics',
        backstory='You are an expert researcher specializing in finding and explaining YouTube content.',
        tools=[youtube_tool],
        verbose=True,
        llm=llm  # Set the specific LLM here
    )

    research_task = Task(
        description=f'Search for and explain video',
        expected_output='Provide a detailed explanation and analysis of the video content',
        agent=researcher
    )

    return Crew(
        agents=[researcher],
        tasks=[research_task],
        verbose=2,
        process=Process.sequential
    )

def main():
    try:
        # Get user input
        youtube_video_url = input("Enter the YouTube video URL (optional, press Enter to skip): ").strip() or None

        # Set up a specific LLM using ChatOpenAI
        custom_llm = ChatOpenAI(
            temperature=0.7,
            model="gpt-4o-mini",
        )

        # Create and run the crew with the custom LLM
        crew = create_youtube_search_crew(youtube_video_url, llm=custom_llm)
        result = crew.kickoff()

        # Extract the string representation of the result
        result_string = str(result)

        print("\nSearch Results:")
        print(result_string)

        # Write results to a file
        output_file = write_to_file(result_string)
        print(f"\nResults have been saved to: {output_file}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()