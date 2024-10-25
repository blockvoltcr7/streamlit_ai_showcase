from typing import List
from datetime import datetime
from pydantic import BaseModel, Field
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool

# Pydantic models remain the same
class ContentPiece(BaseModel):
    caption: str = Field(..., description="The Instagram post caption")
    hashtags: List[str] = Field(..., description="List of relevant hashtags")
    post_timing: str = Field(..., description="Recommended posting time")
    key_messaging: List[str] = Field(..., description="Key messages incorporated in the post")

class ContentStrategy(BaseModel):
    content_pieces: List[ContentPiece] = Field(..., description="List of content pieces")
    posting_schedule: List[str] = Field(..., description="Recommended posting schedule")
    engagement_strategy: str = Field(..., description="Strategy for engaging with responses")

# Initialize tools
search_tool = SerperDevTool()

# Agents remain the same
brand_analyst = Agent(
    role='Brand Voice Analyst',
    goal='Analyze brand guidelines and event details to extract key messaging points and tone requirements',
    backstory="""You are an experienced brand strategist who excels at understanding 
    and maintaining brand voice consistency. You have a keen eye for detail and ensure 
    all content aligns perfectly with brand guidelines.""",
    tools=[search_tool],
    verbose=True
)

content_creator = Agent(
    role='Instagram Content Specialist',
    goal='Create engaging Instagram content that promotes events while maintaining brand voice',
    backstory="""You are a skilled social media content creator with expertise in 
    crafting viral Instagram posts. You understand how to balance promotional content 
    with engagement and brand authenticity.""",
    tools=[search_tool],
    verbose=True
)

content_strategist = Agent(
    role='Content Strategy Expert',
    goal='Develop a strategic posting plan that maximizes event promotion impact',
    backstory="""You are a strategic content planner who understands Instagram's algorithm 
    and optimal posting times. You excel at creating content schedules that maximize reach 
    and engagement.""",
    tools=[search_tool],
    verbose=True
)

# Tasks remain the same but with correct context handling
brand_analysis_task = Task(
    description="""
    Analyze the provided brand guidelines and event details document. Extract and list:
    1. Key brand voice characteristics
    2. Tone requirements
    3. Any specific language or phrases to use/avoid
    4. Event-specific messaging requirements
    5. Target audience characteristics
    """,
    agent=brand_analyst,
    expected_output="Detailed analysis of brand voice and event messaging requirements"
)

content_creation_task = Task(
    description="""
    Using the brand analysis, create 3-5 Instagram posts for the event. Each post should include:
    1. Engaging caption that aligns with brand voice
    2. Relevant hashtags (both brand-specific and event-related)
    3. Key messages about the event
    4. Call to action
    """,
    agent=content_creator,
    expected_output="3-5 complete Instagram posts with captions and hashtags"
)

strategy_task = Task(
    description="""
    Create a posting strategy for the event promotion content. Include:
    1. Optimal posting schedule (dates and times)
    2. Engagement strategy (how to respond to comments and DMs)
    3. Hashtag strategy (when and how to use different hashtag groups)
    4. Cross-promotion recommendations
    """,
    agent=content_strategist,
    output_pydantic=ContentStrategy,
    expected_output="Complete posting and engagement strategy"
)

# Create the crew with sequential process
instagram_event_crew = Crew(
    agents=[brand_analyst, content_creator, content_strategist],
    tasks=[brand_analysis_task, content_creation_task, strategy_task],
    verbose=2,
    process=Process.sequential  # Explicitly set sequential process
)

def create_event_content(brand_guidelines: str, event_details: str) -> ContentStrategy:
    """
    Generate Instagram content and strategy for an event.
    
    Args:
        brand_guidelines (str): Document containing brand voice, tone, and guidelines
        event_details (str): Document containing event information
        
    Returns:
        ContentStrategy: Structured output containing content and strategy
    """
    # Execute the crew with all inputs at once
    result = instagram_event_crew.kickoff(
        inputs={
            "brand_guidelines": brand_guidelines,
            "event_details": event_details
        }
    )
    
    # Return the final result
    return result.pydantic

# Add visualization capability
def visualize_crew_workflow(crew, output_path: str = "crew_workflow.html"):
    """Generate and open a visualization of the crew's workflow."""
    crew.plot(output_path)
    print(f"Workflow visualization has been saved to: {output_path}")

if __name__ == "__main__":
    # Example brand guidelines and event details
    brand_guidelines = """
    Brand: Wellness Cafe
    Voice: Warm, welcoming, health-conscious
    Tone: Encouraging, educational, friendly
    Key Messages: 
    - Focus on holistic wellness
    - Community-driven approach
    - Quality organic ingredients
    - Sustainable practices
    Visual Style:
    - Earth tones
    - Natural lighting
    - Clean, minimal aesthetic
    """
    
    event_details = """
    Event: Summer Wellness Workshop
    Date: July 15th, 2024
    Time: 10 AM - 2 PM
    Location: Wellness Cafe - Downtown Location
    Details:
    - Interactive cooking demonstrations
    - Nutrition workshop
    - Yoga session
    - Organic tea tasting
    Ticket Price: $75 early bird, $90 regular
    Goal: Drive early bird ticket sales and create buzz
    """
    
    # Generate visualization first
    visualize_crew_workflow(instagram_event_crew)
    
    # Generate content and strategy
    try:
        content_strategy = create_event_content(brand_guidelines, event_details)
        print("\nContent Strategy Generated Successfully!")
        print("\nContent Pieces:", len(content_strategy.content_pieces))
        print("Posting Schedule:", content_strategy.posting_schedule)
        print("\nEngagement Strategy:", content_strategy.engagement_strategy)
    except Exception as e:
        print(f"An error occurred: {str(e)}")