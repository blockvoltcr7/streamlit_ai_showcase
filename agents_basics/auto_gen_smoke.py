import os  # Importing the os module to interact with the operating system

import autogen  # Importing the autogen module for creating AutoGen agents
from dotenv import (
    load_dotenv,
)  # Importing load_dotenv to load environment variables from a .env file

# Load environment variables from the .env file
load_dotenv()


def create_config(llm_choice="gpt-4o-mini"):
    """
    Create a configuration for AutoGen agents based on the chosen LLM.

    Args:
    llm_choice (str): The model choice for the LLM. Options are:
                      'gpt-4o-mini' for OpenAI GPT-4 mini model,
                      'gpt4o' for OpenAI GPT-4 model.

    Returns:
    dict: A dictionary containing the model configuration for AutoGen agents,
          including the model name and API key.
    """
    # Determine the configuration based on the chosen LLM
    if llm_choice == "gpt-4o-mini":
        config = {"model": "gpt-4o-mini", "api_key": os.getenv("OPENAI_API_KEY")}
    elif llm_choice == "gpt4o":
        config = {"model": "gpt-4o", "api_key": os.getenv("OPENAI_API_KEY")}
    else:
        # Raise an error if an invalid LLM choice is provided
        raise ValueError("Invalid LLM choice. Choose 'gpt-4o-mini' or 'gpt-4o'")

    return config  # Return the configuration dictionary


def create_agents(config):
    """
    Create AutoGen agents using the provided configuration.

    Args:
    config (dict): Configuration for the LLM, including model and API key.

    Returns:
    tuple: A tuple containing two agents:
           - Assistant agent (AI_Assistant)
           - User proxy agent (Human)
    """
    # Create an Assistant agent with a specific system message
    assistant = autogen.AssistantAgent(
        name="AI_Assistant",
        llm_config={"config_list": [config]},  # Pass the configuration for the LLM
        system_message="You are an expert Software Development Engineer In test (SDET) interacting as an AI assistant.",
    )

    # Create a User proxy agent with a specific system message
    user_proxy = autogen.UserProxyAgent(
        name="Human",
        human_input_mode="TERMINATE",  # Set the input mode to terminate the conversation
        max_consecutive_auto_reply=1,  # Limit the number of consecutive auto replies
        code_execution_config={
            "work_dir": "coding",  # Set the working directory for code execution
            "use_docker": False,  # Disable Docker usage for code execution
        },
        llm_config={"config_list": [config]},  # Pass the configuration for the LLM
        system_message="You are a human interacting as a user proxy learning test automation and software development.",
    )

    return assistant, user_proxy  # Return both agents as a tuple


def main():
    """
    Main function to create configurations and initiate interactions with the agents.
    """
    # Create configurations for the chosen LLM
    open_ai_config = create_config("gpt-4o-mini")

    # Create agents using the specified configuration
    gpt4_assistant, gpt4_user_proxy = create_agents(open_ai_config)
    gpt_3_5_assistant, gpt3_5_user_proxy = create_agents(open_ai_config)

    # Example usage with GPT-4
    print("Interaction with GPT-4 Agent:")
    gpt4_user_proxy.initiate_chat(
        gpt4_assistant,
        message="what is the importance of always creating a test plan instead of directly reading the requirements and just creating test cases? TERMINATE",
    )

    # Example usage with GPT-3.5
    print("Interaction with GPT-3.5 Agent:")
    gpt3_5_user_proxy.initiate_chat(
        gpt_3_5_assistant,
        message="what are the risks of not testing in software development TERMINATE",
    )


if __name__ == "__main__":
    main()  # Execute the main function when the script is run
