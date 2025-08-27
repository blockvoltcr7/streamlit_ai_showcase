"""
Test the Instagram Post Analyzer with sample data
"""

import json
from instagram_post_analyzer import analyze_instagram_posts

def create_sample_data():
    """Create sample Instagram data matching the schema you provided"""
    return {
        "data": {
            "count": 6255,
            "posts": [
                {
                    "node": {
                        "__typename": "GraphSidecar",
                        "id": "3439159241662512720",
                        "gating_info": None,
                        "fact_check_overall_rating": None,
                        "fact_check_information": None,
                        "media_overlay_info": None,
                        "sensitivity_friction_info": None,
                        "sharing_friction_info": {
                            "should_have_sharing_friction": False,
                            "bloks_app_url": None
                        },
                        "dimensions": {
                            "height": 1346,
                            "width": 1080
                        },
                        "display_url": "https://instagram.fcai2-1.fna.fbcdn.net/sample1.jpg",
                        "is_video": False,
                        "tracking_token": "sample_token",
                        "has_upcoming_event": False,
                        "edge_media_to_tagged_user": {"edges": []},
                        "accessibility_caption": None,
                        "edge_media_to_caption": {
                            "edges": [
                                {
                                    "node": {
                                        "text": "🧁 Sweet treats for a sweet day! #cupcakes #dessert"
                                    }
                                }
                            ]
                        },
                        "shortcode": "C-6WRvdS75Q",
                        "edge_media_to_comment": {
                            "count": 4653,
                            "page_info": {
                                "has_next_page": True,
                                "end_cursor": ""
                            }
                        },
                        "edge_media_to_sponsor_user": {"edges": []},
                        "is_affiliate": False,
                        "is_paid_partnership": False,
                        "comments_disabled": False,
                        "taken_at_timestamp": 1724199751,
                        "edge_media_preview_like": {
                            "count": 642848,
                            "edges": []
                        },
                        "owner": {
                            "id": "18428658",
                            "username": "kimkardashian"
                        },
                        "location": None,
                        "nft_asset_info": None,
                        "viewer_has_liked": False,
                        "viewer_has_saved": False,
                        "viewer_has_saved_to_collection": False,
                        "viewer_in_photo_of_you": False,
                        "viewer_can_reshare": True,
                        "thumbnail_src": "https://instagram.fcai2-1.fna.fbcdn.net/thumbnail1.jpg",
                        "coauthor_producers": [],
                        "pinned_for_users": [],
                        "edge_sidecar_to_children": {
                            "edges": [
                                {
                                    "node": {
                                        "__typename": "GraphImage",
                                        "id": "3439159231763742324",
                                        "display_url": "https://instagram.fcai2-1.fna.fbcdn.net/carousel1.jpg",
                                        "is_video": False
                                    }
                                },
                                {
                                    "node": {
                                        "__typename": "GraphImage", 
                                        "id": "3439159231755446953",
                                        "display_url": "https://instagram.fcai2-1.fna.fbcdn.net/carousel2.jpg",
                                        "is_video": False
                                    }
                                }
                            ]
                        }
                    }
                },
                {
                    "node": {
                        "__typename": "GraphVideo",
                        "id": "3439159241662512721",
                        "shortcode": "C-6WRvdS76R",
                        "taken_at_timestamp": 1724199800,
                        "is_video": True,
                        "display_url": "https://instagram.fcai2-1.fna.fbcdn.net/video1.mp4",
                        "edge_media_to_caption": {
                            "edges": [
                                {
                                    "node": {
                                        "text": "Behind the scenes magic ✨ #BTS #filming"
                                    }
                                }
                            ]
                        },
                        "edge_media_preview_like": {"count": 890234},
                        "edge_media_to_comment": {"count": 12456},
                        "owner": {
                            "id": "18428658",
                            "username": "kimkardashian"
                        }
                    }
                },
                {
                    "node": {
                        "__typename": "GraphImage",
                        "id": "3439159241662512722",
                        "shortcode": "C-6WRvdS77S",
                        "taken_at_timestamp": 1724199900,
                        "is_video": False,
                        "display_url": "https://instagram.fcai2-1.fna.fbcdn.net/single_image.jpg",
                        "edge_media_to_caption": {
                            "edges": [
                                {
                                    "node": {
                                        "text": "Golden hour vibes 🌅 #sunset #photography"
                                    }
                                }
                            ]
                        },
                        "edge_media_preview_like": {"count": 1234567},
                        "edge_media_to_comment": {"count": 8901},
                        "owner": {
                            "id": "18428658",
                            "username": "kimkardashian"
                        }
                    }
                }
            ],
            "last_cursor": "QVFDbnZzcllvOW56YTZtUExNd2JuVV9nZXNyLTdoOVl1cTFSQmtkbzFRdXY5R0p1bXFvdEs5T21taGZ0THY5SWxhYk9weU84bjFPb21xbEQ4Q0NoS284aA=="
        }
    }

def test_analysis_capabilities():
    """Test different analysis capabilities"""
    print("🧪 Testing Instagram Post Analyzer")
    print("=" * 50)
    
    # Create sample data
    sample_data = create_sample_data()
    
    # Show data overview
    posts = sample_data['data']['posts']
    print(f"📊 Sample data contains {len(posts)} posts")
    print(f"👤 User: @{posts[0]['node']['owner']['username']}")
    print(f"📈 Total posts available: {sample_data['data']['count']:,}")
    
    # Test questions
    test_questions = [
        "How many posts are in this dataset and what's the total engagement?",
        "Which post has the most likes and what is it about?",
        "What types of content are posted (videos vs images vs carousels)?",
        "What are the main themes in the captions?",
        "Compare the engagement rates across different post types",
        "When were these posts created?",
        "What's the average number of likes and comments per post?"
    ]
    
    print(f"\n🤖 Testing {len(test_questions)} analysis scenarios...")
    print("=" * 50)
    
    # Note: This will require OpenAI API key to work
    print("⚠️  Note: To run the actual AI analysis, you need to:")
    print("1. Add your OpenAI API key to the .env file")
    print("2. Replace 'your_openai_api_key_here' with your actual key")
    print("\nFor now, showing the structured data that would be analyzed:")
    
    # Show what data is available for analysis
    print("\n📋 Available Data Structure:")
    for i, post in enumerate(posts, 1):
        node = post['node']
        caption = ""
        if 'edge_media_to_caption' in node and node['edge_media_to_caption']['edges']:
            caption = node['edge_media_to_caption']['edges'][0]['node']['text']
        
        print(f"\nPost {i}:")
        print(f"  • Type: {node['__typename']} ({'Video' if node['is_video'] else 'Image/Carousel'})")
        print(f"  • Shortcode: {node['shortcode']}")
        print(f"  • Likes: {node['edge_media_preview_like']['count']:,}")
        print(f"  • Comments: {node['edge_media_to_comment']['count']:,}")
        print(f"  • Caption: {caption}")
        if 'edge_sidecar_to_children' in node:
            print(f"  • Carousel with {len(node['edge_sidecar_to_children']['edges'])} images")
    
    print("\n" + "=" * 50)
    print("📝 Example Questions the AI Agent Can Answer:")
    for i, question in enumerate(test_questions, 1):
        print(f"{i}. {question}")

if __name__ == "__main__":
    test_analysis_capabilities()
