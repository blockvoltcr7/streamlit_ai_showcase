"""
Instagram Post Analysis Agent using Pydantic AI

This module creates an AI agent that can analyze Instagram posts from EnsembleData API responses
and answer questions about the content, engagement metrics, and other post attributes.
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class InstagramPostData(BaseModel):
    """Structured model for Instagram post data"""
    post_id: str = Field(description="Unique post identifier")
    shortcode: str = Field(description="Instagram shortcode for the post")
    username: str = Field(description="Username of the post owner")
    user_id: str = Field(description="User ID of the post owner")
    caption: str = Field(description="Post caption/text content")
    like_count: int = Field(description="Number of likes on the post")
    comment_count: int = Field(description="Number of comments on the post")
    is_video: bool = Field(description="Whether the post is a video")
    taken_at_timestamp: int = Field(description="Unix timestamp when the post was created")
    image_urls: List[str] = Field(description="List of image URLs in the post")
    post_type: str = Field(description="Type of post (e.g., GraphSidecar, GraphImage)")
    has_multiple_images: bool = Field(description="Whether the post has multiple images/carousel")

class AnalysisResult(BaseModel):
    """Structured response for analysis results"""
    answer: str = Field(description="Direct answer to the user's question")
    supporting_data: Optional[Dict[str, Any]] = Field(description="Additional data supporting the answer")
    confidence: str = Field(description="Confidence level of the analysis")

# Create the Instagram analysis agent
instagram_agent = Agent(
    'openai:gpt-4o',
    deps_type=Dict[str, Any],  # The raw Instagram API response
    output_type=AnalysisResult,
    system_prompt="""
    You are an expert Instagram post analyzer. You receive Instagram post data from the EnsembleData API 
    and can answer detailed questions about posts, engagement metrics, content analysis, and user behavior.
    
    You have access to comprehensive post data including:
    - Post metadata (ID, shortcode, timestamps)
    - User information (username, user ID)
    - Engagement metrics (likes, comments)
    - Content details (captions, images, videos)
    - Technical details (post type, dimensions, URLs)
    
    Provide accurate, insightful answers based on the data available. If asked about trends or comparisons, 
    focus on the data provided. Be specific and cite actual numbers when relevant.
    
    Always structure your response with a clear answer and supporting data when applicable.
    """
)

@instagram_agent.tool
def extract_post_data(ctx: RunContext[Dict[str, Any]]) -> List[InstagramPostData]:
    """Extract and structure Instagram post data from the API response"""
    raw_data = ctx.deps
    posts = []
    
    if 'data' in raw_data and 'posts' in raw_data['data']:
        for post_item in raw_data['data']['posts']:
            node = post_item['node']
            
            # Extract caption
            caption = ""
            if 'edge_media_to_caption' in node and node['edge_media_to_caption']['edges']:
                caption = node['edge_media_to_caption']['edges'][0]['node']['text']
            
            # Extract image URLs
            image_urls = []
            if 'display_url' in node:
                image_urls.append(node['display_url'])
            
            # Add carousel images if present
            if 'edge_sidecar_to_children' in node:
                for child in node['edge_sidecar_to_children']['edges']:
                    if 'display_url' in child['node']:
                        image_urls.append(child['node']['display_url'])
            
            post_data = InstagramPostData(
                post_id=node['id'],
                shortcode=node['shortcode'],
                username=node['owner']['username'],
                user_id=node['owner']['id'],
                caption=caption,
                like_count=node['edge_media_preview_like']['count'],
                comment_count=node['edge_media_to_comment']['count'],
                is_video=node['is_video'],
                taken_at_timestamp=node['taken_at_timestamp'],
                image_urls=image_urls,
                post_type=node['__typename'],
                has_multiple_images=len(image_urls) > 1
            )
            posts.append(post_data)
    
    return posts

@instagram_agent.tool
def get_engagement_metrics(ctx: RunContext[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate engagement metrics and statistics"""
    posts = extract_post_data(ctx)
    
    if not posts:
        return {"error": "No posts found"}
    
    total_likes = sum(post.like_count for post in posts)
    total_comments = sum(post.comment_count for post in posts)
    total_posts = len(posts)
    
    avg_likes = total_likes / total_posts if total_posts > 0 else 0
    avg_comments = total_comments / total_posts if total_posts > 0 else 0
    
    # Find most engaging post
    most_liked_post = max(posts, key=lambda p: p.like_count)
    most_commented_post = max(posts, key=lambda p: p.comment_count)
    
    return {
        "total_posts": total_posts,
        "total_likes": total_likes,
        "total_comments": total_comments,
        "average_likes": round(avg_likes, 2),
        "average_comments": round(avg_comments, 2),
        "most_liked_post": {
            "shortcode": most_liked_post.shortcode,
            "likes": most_liked_post.like_count,
            "caption_preview": most_liked_post.caption[:100] + "..." if len(most_liked_post.caption) > 100 else most_liked_post.caption
        },
        "most_commented_post": {
            "shortcode": most_commented_post.shortcode,
            "comments": most_commented_post.comment_count,
            "caption_preview": most_commented_post.caption[:100] + "..." if len(most_commented_post.caption) > 100 else most_commented_post.caption
        }
    }

@instagram_agent.tool
def analyze_content_types(ctx: RunContext[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze the types of content in the posts"""
    posts = extract_post_data(ctx)
    
    if not posts:
        return {"error": "No posts found"}
    
    video_count = sum(1 for post in posts if post.is_video)
    image_count = sum(1 for post in posts if not post.is_video)
    carousel_count = sum(1 for post in posts if post.has_multiple_images)
    single_image_count = sum(1 for post in posts if not post.is_video and not post.has_multiple_images)
    
    post_types = {}
    for post in posts:
        post_type = post.post_type
        post_types[post_type] = post_types.get(post_type, 0) + 1
    
    return {
        "total_posts": len(posts),
        "videos": video_count,
        "images": image_count,
        "carousels": carousel_count,
        "single_images": single_image_count,
        "post_types": post_types,
        "content_distribution": {
            "video_percentage": round((video_count / len(posts)) * 100, 1),
            "image_percentage": round((image_count / len(posts)) * 100, 1),
            "carousel_percentage": round((carousel_count / len(posts)) * 100, 1)
        }
    }

@instagram_agent.tool
def get_posting_patterns(ctx: RunContext[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze posting patterns and timestamps"""
    posts = extract_post_data(ctx)
    
    if not posts:
        return {"error": "No posts found"}
    
    # Convert timestamps to datetime objects
    post_times = []
    for post in posts:
        dt = datetime.fromtimestamp(post.taken_at_timestamp)
        post_times.append({
            "shortcode": post.shortcode,
            "datetime": dt,
            "hour": dt.hour,
            "day_of_week": dt.strftime("%A"),
            "date": dt.strftime("%Y-%m-%d")
        })
    
    # Analyze posting hours
    hour_distribution = {}
    for pt in post_times:
        hour = pt["hour"]
        hour_distribution[hour] = hour_distribution.get(hour, 0) + 1
    
    # Analyze day of week
    day_distribution = {}
    for pt in post_times:
        day = pt["day_of_week"]
        day_distribution[day] = day_distribution.get(day, 0) + 1
    
    # Find most active posting times
    most_active_hour = max(hour_distribution.items(), key=lambda x: x[1]) if hour_distribution else None
    most_active_day = max(day_distribution.items(), key=lambda x: x[1]) if day_distribution else None
    
    return {
        "total_posts_analyzed": len(posts),
        "date_range": {
            "earliest": min(pt["date"] for pt in post_times),
            "latest": max(pt["date"] for pt in post_times)
        },
        "hour_distribution": hour_distribution,
        "day_distribution": day_distribution,
        "most_active_hour": f"{most_active_hour[0]}:00 ({most_active_hour[1]} posts)" if most_active_hour else None,
        "most_active_day": f"{most_active_day[0]} ({most_active_day[1]} posts)" if most_active_day else None
    }

@instagram_agent.tool
def search_posts_by_criteria(ctx: RunContext[Dict[str, Any]], 
                           min_likes: Optional[int] = None,
                           min_comments: Optional[int] = None,
                           content_type: Optional[str] = None,
                           keyword_in_caption: Optional[str] = None) -> List[Dict[str, Any]]:
    """Search and filter posts based on specific criteria"""
    posts = extract_post_data(ctx)
    
    filtered_posts = []
    for post in posts:
        # Apply filters
        if min_likes and post.like_count < min_likes:
            continue
        if min_comments and post.comment_count < min_comments:
            continue
        if content_type:
            if content_type.lower() == "video" and not post.is_video:
                continue
            if content_type.lower() == "image" and post.is_video:
                continue
            if content_type.lower() == "carousel" and not post.has_multiple_images:
                continue
        if keyword_in_caption and keyword_in_caption.lower() not in post.caption.lower():
            continue
        
        # Add to results
        filtered_posts.append({
            "shortcode": post.shortcode,
            "username": post.username,
            "likes": post.like_count,
            "comments": post.comment_count,
            "is_video": post.is_video,
            "has_multiple_images": post.has_multiple_images,
            "caption_preview": post.caption[:150] + "..." if len(post.caption) > 150 else post.caption,
            "posted_date": datetime.fromtimestamp(post.taken_at_timestamp).strftime("%Y-%m-%d %H:%M")
        })
    
    return filtered_posts

def analyze_instagram_posts(instagram_data: Dict[str, Any], question: str) -> AnalysisResult:
    """
    Main function to analyze Instagram posts and answer questions
    
    Args:
        instagram_data: Raw response from EnsembleData Instagram API
        question: User's question about the posts
        
    Returns:
        AnalysisResult with answer and supporting data
    """
    result = instagram_agent.run_sync(question, deps=instagram_data)
    return result.output

# Example usage and test function
def test_agent_with_sample_data():
    """Test the agent with sample Instagram data"""
    # Sample data structure (simplified version of your schema)
    sample_data = {
        "data": {
            "count": 6255,
            "posts": [
                {
                    "node": {
                        "__typename": "GraphSidecar",
                        "id": "3439159241662512720",
                        "shortcode": "C-6WRvdS75Q",
                        "taken_at_timestamp": 1724199751,
                        "is_video": False,
                        "edge_media_to_caption": {
                            "edges": [{"node": {"text": "🧁"}}]
                        },
                        "edge_media_preview_like": {"count": 642848},
                        "edge_media_to_comment": {"count": 4653},
                        "owner": {"id": "18428658", "username": "kimkardashian"},
                        "display_url": "https://example.com/image1.jpg",
                        "edge_sidecar_to_children": {
                            "edges": [
                                {"node": {"display_url": "https://example.com/image1.jpg"}},
                                {"node": {"display_url": "https://example.com/image2.jpg"}}
                            ]
                        }
                    }
                }
            ]
        }
    }
    
    # Test questions
    questions = [
        "What's the engagement rate of these posts?",
        "How many likes does the most popular post have?",
        "What type of content performs best?",
        "When was this post created?",
        "Who is the author of these posts?"
    ]
    
    for question in questions:
        print(f"\nQuestion: {question}")
        try:
            result = analyze_instagram_posts(sample_data, question)
            print(f"Answer: {result.answer}")
            if result.supporting_data:
                print(f"Supporting Data: {json.dumps(result.supporting_data, indent=2)}")
            print(f"Confidence: {result.confidence}")
        except Exception as e:
            print(f"Error: {e}")
        print("-" * 50)

if __name__ == "__main__":
    # Set OpenAI API key from environment
    if not os.getenv("OPENAI_API_KEY"):
        print("Warning: OPENAI_API_KEY not found in environment variables")
    
    test_agent_with_sample_data()
