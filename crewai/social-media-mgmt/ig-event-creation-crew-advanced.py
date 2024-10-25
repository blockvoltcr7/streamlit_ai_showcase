from typing import List, Optional, Dict
from datetime import datetime
from pydantic import BaseModel, Field
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool, BaseTool
import json

import os
import webbrowser
from urllib.request import pathname2url

def visualize_crew_workflow(crew, filename: str = "crew_workflow.html"):
    """
    Generate and display a visualization of the crew's workflow.

    Args:
        crew: The CrewAI crew instance
        filename: Name of the HTML file to be saved
    """
    # Create the directory path
    dir_path = os.path.join(os.getcwd(), "crewai", "social-media-mgmt", "html")

    # Ensure the directory exists
    os.makedirs(dir_path, exist_ok=True)

    # Create the full file path
    output_path = os.path.join(dir_path, filename)
    # Generate the workflow visualization
    crew.plot(output_path)

    # Get the absolute path and convert it to a URL
    abs_path = os.path.abspath(output_path)
    url = 'file:' + pathname2url(abs_path)

    # Open the visualization in the default browser
    webbrowser.open(url, new=2)

    print(f"Workflow visualization has been saved to: {abs_path}")

# Enhanced Pydantic Models with Review States
class ContentPiece(BaseModel):
    caption: str = Field(..., description="The Instagram post caption")
    hashtags: List[str] = Field(..., description="List of relevant hashtags")
    post_timing: str = Field(..., description="Recommended posting time")
    key_messaging: List[str] = Field(..., description="Key messages incorporated in the post")
    review_status: str = Field(default="pending", description="Current review status")
    feedback: Optional[str] = Field(default=None, description="Feedback from reviewer")
    revision_history: List[Dict] = Field(default_list, description="History of revisions")

class ContentStrategy(BaseModel):
    content_pieces: List[ContentPiece] = Field(..., description="List of content pieces")
    posting_schedule: List[str] = Field(..., description="Recommended posting schedule")
    engagement_strategy: str = Field(..., description="Strategy for engaging with responses")
    target_metrics: Dict[str, float] = Field(..., description="Target engagement metrics")
    review_status: str = Field(default="pending", description="Overall review status")
    feedback_summary: Optional[str] = Field(default=None, description="Summary of all feedback")

# Custom Tools
class HashtagAnalyzerTool(BaseTool):
    name: str = "Hashtag Analyzer"
    description: str = "Analyzes hashtag relevance, reach potential, and brand alignment"

    def _run(self, hashtags: List[str], brand_guidelines: str) -> dict:
        """Analyze hashtags for effectiveness and brand alignment."""
        # Implement hashtag analysis logic here
        return {
            "relevant_hashtags": hashtags,
            "reach_potential": "high",
            "brand_alignment": "strong"
        }

class ContentQualityCheckerTool(BaseTool):
    name: str = "Content Quality Checker"
    description: str = "Checks content against brand guidelines and best practices"

    def _run(self, content: str, brand_guidelines: str) -> dict:
        """Check content quality and brand alignment."""
        # Implement content checking logic here
        return {
            "tone_match": True,
            "brand_voice_alignment": "high",
            "suggested_improvements": []
        }

# Initialize tools
search_tool = SerperDevTool()
hashtag_analyzer = HashtagAnalyzerTool()
quality_checker = ContentQualityCheckerTool()

# Enhanced Agents with Specialized Roles
brand_analyst = Agent(
    role='Brand Voice Analyst',
    goal='Analyze brand guidelines and ensure perfect alignment of all content',
    backstory="""You are a premier brand strategist with 15+ years of experience in 
    maintaining brand consistency across social media platforms. You've worked with 
    major global brands and have a reputation for catching even the smallest brand 
    voice deviations.""",
    tools=[search_tool, quality_checker],
    verbose=True
)

content_creator = Agent(
    role='Instagram Content Specialist',
    goal='Create engaging, on-brand content that drives event attendance',
    backstory="""You are an award-winning social media content creator known for 
    crafting viral Instagram posts that maintain authentic brand voice. You've helped 
    numerous events sell out through strategic content creation.""",
    tools=[search_tool, hashtag_analyzer],
    verbose=True
)

content_strategist = Agent(
    role='Content Strategy Expert',
    goal='Develop data-driven posting strategies that maximize reach and engagement',
    backstory="""You are a strategic content planner who has mastered Instagram's 
    algorithm. Your posting strategies consistently achieve 3x average engagement rates.""",
    tools=[search_tool],
    verbose=True
)

quality_assurance = Agent(
    role='Quality Assurance Manager',
    goal='Ensure all content meets brand standards and maximizes impact',
    backstory="""You are a detail-oriented QA specialist with a background in brand 
    management and social media optimization. You've prevented numerous brand voice 
    inconsistencies and helped improve content performance by 150%.""",
    tools=[quality_checker, hashtag_analyzer],
    verbose=True,
    allow_delegation=True
)

# Enhanced Tasks with Review Loops
brand_analysis_task = Task(
    description="""
    Perform a comprehensive brand and event analysis:
    1. Deep dive into brand voice characteristics and evolution
    2. Identify core brand values and messaging pillars
    3. Map event goals to brand strategy
    4. Create a brand voice consistency checklist
    5. Develop event-specific messaging guidelines
    
    Input Document: {brand_guidelines}
    Event Details: {event_details}
    """,
    agent=brand_analyst,
    expected_output="Detailed brand and event analysis with messaging guidelines"
)

content_creation_task = Task(
    description="""
    Create a suite of Instagram content for the event:
    1. 5-7 main feed posts with carousel options
    2. 3-5 story sequences
    3. Key messaging points for each piece
    4. Strategic hashtag groups
    
    Use brand analysis: {previous_task_output}
    Event Details: {event_details}
    
    Request feedback from QA before finalizing.
    """,
    agent=content_creator,
    expected_output="Complete Instagram content suite with multiple content types"
)

content_review_task = Task(
    description="""
    Review all created content against brand guidelines and performance metrics:
    1. Check brand voice consistency
    2. Verify message accuracy
    3. Assess engagement potential
    4. Validate hashtag strategy
    5. Provide specific feedback for improvements
    
    Content to review: {previous_task_output}
    Brand Guidelines: {brand_guidelines}
    """,
    agent=quality_assurance,
    expected_output="Detailed review feedback and improvement suggestions"
)

content_revision_task = Task(
    description="""
    Revise content based on QA feedback:
    1. Address all feedback points
    2. Maintain creative integrity
    3. Strengthen brand alignment
    4. Enhance engagement potential
    
    Original Content: {content}
    Feedback: {feedback}
    """,
    agent=content_creator,
    expected_output="Revised content incorporating all feedback"
)

strategy_task = Task(
    description="""
    Develop a comprehensive posting strategy:
    1. Data-driven posting schedule
    2. Engagement response templates
    3. Performance monitoring plan
    4. Contingency content recommendations
    5. Cross-promotion strategy
    
    Use final content: {previous_task_output}
    Event Details: {event_details}
    """,
    agent=content_strategist,
    output_pydantic=ContentStrategy,
    expected_output="Complete content strategy with backup plans"
)

final_review_task = Task(
    description="""
    Perform final quality assurance review:
    1. Verify all feedback has been addressed
    2. Confirm brand consistency
    3. Validate strategy feasibility
    4. Check for any missed opportunities
    
    Content and Strategy: {previous_task_output}
    Original Requirements: {brand_guidelines}
    Event Details: {event_details}
    """,
    agent=quality_assurance,
    expected_output="Final approval or additional revision requirements"
)

# Create the advanced crew with hierarchical process
instagram_event_crew = Crew(
    agents=[brand_analyst, content_creator, content_strategist, quality_assurance],
    tasks=[
        brand_analysis_task,
        content_creation_task,
        content_review_task,
        content_revision_task,
        strategy_task,
        final_review_task
    ],
    verbose=2,
    process=Process.hierarchical,
    manager_agent=quality_assurance
)

def create_event_content_with_review(
    brand_guidelines: str,
    event_details: str,
    max_revision_rounds: int = 2
) -> ContentStrategy:
    """
    Generate Instagram content and strategy with review loops.
    
    Args:
        brand_guidelines (str): Document containing brand voice, tone, and guidelines
        event_details (str): Document containing event information
        max_revision_rounds (int): Maximum number of revision rounds
        
    Returns:
        ContentStrategy: Structured output containing approved content and strategy
    """
    current_round = 0
    final_approval = False
    
    while current_round < max_revision_rounds and not final_approval:
        result = instagram_event_crew.kickoff(
            inputs={
                "brand_guidelines": brand_guidelines,
                "event_details": event_details,
                "revision_round": current_round
            }
        )
        
        # Check if content received final approval
        if result.pydantic.review_status == "approved":
            final_approval = True
        else:
            current_round += 1
            print(f"Revision round {current_round} initiated based on feedback")
    
    return result.pydantic

# Example usage and testing

if __name__ == "__main__":
    # Example brand guidelines and event details (same as before)
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
    # Example brand guidelines and event details (same as before)
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
visualize_crew_workflow(instagram_event_crew, "instagram_event_workflow.html")
    - Nutrition workshop
    - Yoga session
    - Organic tea tasting
    Ticket Price: $75 early bird, $90 regular
    Goal: Drive early bird ticket sales and create buzz
    """
    
    # Generate content with review process
    content_strategy = create_event_content_with_review(
        brand_guidelines,
        event_details,
        max_revision_rounds=2
    )
    
    print("Content Strategy Generated and Approved!")
    print(f"Number of content pieces: {len(content_strategy.content_pieces)}")
    print(f"Review Status: {content_strategy.review_status}")
       # After creating the instagram_event_crew, add:
    sys.exit(0)
