import logging

logging.basicConfig(level=logging.DEBUG)

import os

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

slack_token = os.getenv("SLACK_BOT_TOKEN")
print(slack_token)
client = WebClient(token=slack_token)

try:
    response = client.chat_postMessage(
        channel="automations", text="sure, ill remind you"
    )
except SlackApiError as e:
    # You will get a SlackApiError if "ok" is False
    assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
