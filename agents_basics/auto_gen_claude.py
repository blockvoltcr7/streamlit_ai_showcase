import os

import autogen
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def create_anthropic_config(model="claude-3-5-haiku-20241022"):
    """Create a configuration for Anthropic models."""
    return [
        {
            "model": model,
            "api_key": os.getenv("ANTHROPIC_API_KEY"),
            "api_type": "anthropic",
        }
    ]


def create_agent(name, system_message, config_list):
    """Create an AutoGen agent using Anthropic's model."""
    return autogen.AssistantAgent(
        name=name,
        llm_config={"config_list": config_list},
        system_message=system_message,
    )


def main():
    # Create Anthropic configuration
    anthropic_config = create_anthropic_config()

    # Create agents
    assistant = create_agent(
        "Assistant", "You are a helpful AI assistant.", anthropic_config
    )

    user_proxy = autogen.UserProxyAgent(
        "User_Proxy",
        human_input_mode="NEVER",
        code_execution_config={
            "work_dir": "coding",
            "use_docker": False,
        },
        max_consecutive_auto_reply=1,
        is_termination_msg=lambda x: x.get("content", "")
        .rstrip()
        .endswith("TERMINATE"),
    )

    # Initiate the chat
    user_proxy.initiate_chat(
        assistant,
        message="Explain the role of a Software Development Engineer in Test (SDET).",
    )

    # Print the last message from the assistant
    print(assistant.last_message()["content"])


if __name__ == "__main__":
    main()
