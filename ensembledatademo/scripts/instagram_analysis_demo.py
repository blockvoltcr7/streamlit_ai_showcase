"""
Instagram Post Analysis Demo

This script fetches Instagram posts using the EnsembleData API and then uses
a Pydantic AI agent to analyze the data and answer questions about the posts.
"""

import json
import requests
import os
from dotenv import load_dotenv
from instagram_post_analyzer import analyze_instagram_posts, AnalysisResult

# Load environment variables
load_dotenv()

def fetch_instagram_posts(user_id: int = 18428658, depth: int = 1, chunk_size: int = 10) -> dict:
    """
    Fetch Instagram posts using EnsembleData API
    
    Args:
        user_id: Instagram user ID (default: Kim Kardashian)
        depth: How deep to fetch posts
        chunk_size: Number of posts per request
        
    Returns:
        API response data
    """
    root = "https://ensembledata.com/apis"
    endpoint = "/instagram/user/posts"
    
    params = {
        "user_id": user_id,
        "depth": depth,
        "oldest_timestamp": 1666262030,
        "chunk_size": chunk_size,
        "start_cursor": "",
        "alternative_method": False,
        "token": os.getenv("ENSEMBLE_DATA_API")
    }
    
    try:
        response = requests.get(root + endpoint, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def interactive_analysis():
    """
    Interactive session for analyzing Instagram posts
    """
    print("🔍 Instagram Post Analyzer")
    print("=" * 50)
    
    # Check for required API keys
    if not os.getenv("ENSEMBLE_DATA_API"):
        print("❌ Error: ENSEMBLE_DATA_API key not found in .env file")
        return
    
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not found in .env file")
        return
    
    print("✅ API keys found")
    
    # Fetch Instagram data
    print("\n📱 Fetching Instagram posts...")
    user_id = 18428658  # Kim Kardashian's ID
    instagram_data = fetch_instagram_posts(user_id=user_id, chunk_size=5)
    
    if not instagram_data:
        print("❌ Failed to fetch Instagram data")
        return
    
    # Show basic stats
    post_count = len(instagram_data.get('data', {}).get('posts', []))
    total_count = instagram_data.get('data', {}).get('count', 0)
    
    print(f"✅ Successfully fetched {post_count} posts (out of {total_count} total)")
    
    if post_count == 0:
        print("❌ No posts found to analyze")
        return
    
    # Show sample post info
    first_post = instagram_data['data']['posts'][0]['node']
    username = first_post['owner']['username']
    print(f"📊 Analyzing posts from @{username}")
    
    print("\n" + "=" * 50)
    print("🤖 AI Analysis Ready - Ask questions about the posts!")
    print("=" * 50)
    print("\nExample questions you can ask:")
    print("• What's the average engagement rate?")
    print("• Which post has the most likes?")
    print("• What types of content are posted?")
    print("• When do they post most often?")
    print("• Show me posts with more than 500k likes")
    print("• What's in the captions?")
    print("\nType 'quit' to exit")
    print("-" * 50)
    
    # Interactive Q&A loop
    while True:
        question = input("\n💭 Your question: ").strip()
        
        if question.lower() in ['quit', 'exit', 'bye']:
            print("👋 Thanks for using Instagram Post Analyzer!")
            break
        
        if not question:
            continue
        
        print("🤔 Analyzing...")
        
        try:
            result = analyze_instagram_posts(instagram_data, question)
            
            print(f"\n🎯 Answer: {result.answer}")
            
            if result.supporting_data:
                print(f"\n📈 Supporting Data:")
                print(json.dumps(result.supporting_data, indent=2))
            
            print(f"\n🎚️ Confidence: {result.confidence}")
            
        except Exception as e:
            print(f"❌ Error during analysis: {e}")
            print("Please try rephrasing your question or check your API keys.")
        
        print("-" * 50)

def run_predefined_analysis():
    """
    Run a predefined set of analysis questions
    """
    print("🔍 Running Predefined Instagram Analysis")
    print("=" * 50)
    
    # Fetch data
    print("📱 Fetching Instagram posts...")
    instagram_data = fetch_instagram_posts(user_id=18428658, chunk_size=10)
    
    if not instagram_data:
        print("❌ Failed to fetch Instagram data")
        return
    
    post_count = len(instagram_data.get('data', {}).get('posts', []))
    print(f"✅ Fetched {post_count} posts")
    
    # Predefined questions for comprehensive analysis
    questions = [
        "What's the overall engagement performance of these posts?",
        "Which post has the highest engagement and what's it about?",
        "What types of content are being posted (videos, images, carousels)?",
        "What are the posting patterns and optimal times?",
        "Show me the top 3 most liked posts with their details",
        "What can you tell me about the captions and content themes?",
        "How does the comment-to-like ratio look across posts?",
    ]
    
    print(f"\n🤖 Running {len(questions)} analysis questions...")
    print("=" * 50)
    
    for i, question in enumerate(questions, 1):
        print(f"\n{i}. {question}")
        print("-" * 30)
        
        try:
            result = analyze_instagram_posts(instagram_data, question)
            print(f"Answer: {result.answer}")
            
            if result.supporting_data:
                print("Key Data Points:")
                # Show only the most relevant data points
                for key, value in result.supporting_data.items():
                    if isinstance(value, (int, float, str)):
                        print(f"  • {key}: {value}")
                    elif isinstance(value, dict) and len(value) <= 3:
                        print(f"  • {key}: {value}")
            
        except Exception as e:
            print(f"Error: {e}")
        
        print()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--auto":
        run_predefined_analysis()
    else:
        interactive_analysis()
