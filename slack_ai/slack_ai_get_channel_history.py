import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import google.generativeai as genai
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


# Pydantic Models
class BotIcons(BaseModel):
    image_36: str
    image_48: str
    image_72: str


class BotProfile(BaseModel):
    id: str
    deleted: bool
    name: str
    app_id: str
    team_id: str
    updated: int
    icons: Optional[BotIcons] = None


class BlockElement(BaseModel):
    type: str
    elements: List[Dict[str, Any]]


class Block(BaseModel):
    type: str
    block_id: str
    elements: List[BlockElement]


class Message(BaseModel):
    user: str
    type: str
    ts: str
    text: str
    team: Optional[str] = None  # Made optional for channel_join messages
    bot_id: Optional[str] = None
    app_id: Optional[str] = None
    client_msg_id: Optional[str] = None
    bot_profile: Optional[BotProfile] = None
    blocks: Optional[List[Block]] = None
    subtype: Optional[str] = None
    inviter: Optional[str] = None


class SlackResponse(BaseModel):
    ok: bool
    messages: List[Message]
    has_more: bool
    pin_count: int
    channel_actions_ts: Optional[str] = None
    channel_actions_count: int


class SlackClient:
    def __init__(self):
        # Load environment variables
        load_dotenv()

        # Set up logging
        logging.basicConfig(
            level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
        )
        self.logger = logging.getLogger(__name__)

        # Initialize Slack client
        self.slack_token = os.getenv("SLACK_BOT_TOKEN")
        if not self.slack_token:
            raise ValueError("SLACK_BOT_TOKEN not found in environment variables")
        self.client = WebClient(token=self.slack_token)

        # Initialize Gemini
        self.setup_gemini()

    def setup_gemini(self):
        """Initialize Gemini client"""
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
        }
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash-8b",
            generation_config=generation_config,
        )
        self.chat = self.model.start_chat(history=[])

    def get_channel_history(self, channel_id: str) -> Optional[SlackResponse]:
        """
        Fetch and parse channel history using Pydantic models
        """
        try:
            # Call the conversations.history method
            result = self.client.conversations_history(channel=channel_id)

            # Convert the SlackResponse object to dict
            result_dict = result.data

            # Parse response through Pydantic model
            slack_response = SlackResponse.model_validate(result_dict)

            # self.logger.info(
            #     f"{len(slack_response.messages)} messages found in {channel_id}"
            # )

            return slack_response

        except SlackApiError as e:
            self.logger.error(f"Error fetching conversation history: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            return None

    def print_messages(self, response: SlackResponse):
        """
        Print formatted messages from the response
        """
        for msg in response.messages:
            print("\n" + "=" * 50)
            print(f"Timestamp: {msg.ts}")

            if msg.subtype == "channel_join":
                print(f"Event: Channel Join")
                print(f"User: {msg.user}")
                if msg.inviter:
                    print(f"Invited by: {msg.inviter}")
            else:
                print(f"User: {msg.user}")
                print(f"Text: {msg.text}")
                if msg.bot_profile:
                    print(f"Bot Name: {msg.bot_profile.name}")

            print("-" * 50)

    def summarize_conversation(self, messages: List[Message]) -> str:
        """
        Summarize the conversation using Gemini
        """
        # Format messages into a structured conversation
        print(f"structuredmessages: {messages}")
        formatted_convo = self._format_conversation(messages)

        prompt = f"""
        Please analyze this Slack conversation and provide:
        1. A brief summary of the main discussion points
        2. Key action items or decisions made
        3. Any important questions that were raised

        Conversation:
        {formatted_convo}
        """

        try:
            response = self.chat.send_message(prompt)
            return response.text
        except Exception as e:
            self.logger.error(f"Error getting summary from Gemini: {e}")
            return "Error generating summary"

    def _format_conversation(self, messages: List[Message]) -> str:
        """
        Format messages into a readable conversation string
        """
        formatted_msgs = []
        for msg in reversed(messages):  # Reverse to show oldest first
            timestamp = datetime.fromtimestamp(float(msg.ts)).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            sender = msg.bot_profile.name if msg.bot_profile else msg.user
            formatted_msgs.append(f"[{timestamp}] {sender}: {msg.text}")

        return "\n".join(formatted_msgs)


def main():
    # Initialize client
    slack = SlackClient()

    # Channel ID to fetch messages from
    channel_id = "C083L8V82NL"

    # Get channel history
    response = slack.get_channel_history(channel_id)

    if response:
        print("\n=== Channel Messages ===")
        slack.print_messages(response)

        print("\n=== Conversation Summary ===")
        summary = slack.summarize_conversation(response.messages)
        print(summary)


if __name__ == "__main__":
    main()
