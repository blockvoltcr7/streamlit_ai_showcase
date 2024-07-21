import autogen
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def create_config(llm_choice='gpt4'):
    """
    Create a configuration for AutoGen agents based on the chosen LLM.
    
    Args:
    llm_choice (str): 'gpt4' for OpenAI GPT-4 or 'gpt3.5' for OpenAI GPT-3.5
    
    Returns:
    dict: Configuration for AutoGen agents
    """
    if llm_choice == 'gpt4':
        config = {
            "model": "gpt-4-0613",
            "api_key": os.getenv("OPENAI_API_KEY")
        }
    elif llm_choice == 'gpt3.5':
        config = {
            "model": "gpt-3.5-turbo",
            "api_key": os.getenv("OPENAI_API_KEY")
        }
    else:
        raise ValueError("Invalid LLM choice. Choose 'gpt4' or 'gpt3.5'.")
    
    return config

def create_agents(config):
    """
    Create AutoGen agents using the provided configuration.
    
    Args:
    config (dict): Configuration for the LLM
    
    Returns:
    tuple: Assistant agent and User proxy agent
    """
    assistant = autogen.AssistantAgent(
        name="AI_Assistant",
        llm_config={"config_list": [config]},
        system_message="You are an expert Software Development Engineer In test (SDET) interacting as an AI assistant."
    )
    
    user_proxy = autogen.UserProxyAgent(
        name="Human",
        human_input_mode="TERMINATE",
        max_consecutive_auto_reply=1,
        code_execution_config={
            "work_dir": "coding",
            "use_docker": False  # Disable Docker usage
        },
        llm_config={"config_list": [config]},
        system_message="You are a human interacting as a user proxy learning test automation and software development."
    )
    
    return assistant, user_proxy

# The rest of the script remains the same

def main():
    # Create configurations for different LLMs
    open_ai_config = create_config('gpt4')

    # Create agents with different LLMs
    gpt4_assistant, gpt4_user_proxy = create_agents(open_ai_config)
    gpt_3_5_assistant, gpt3_5_user_proxy = create_agents(open_ai_config)

    # Example usage with GPT-4
    print("Interaction with GPT-4 Agent:")
    gpt4_user_proxy.initiate_chat(
        gpt4_assistant,
        message="what is the importance of always creating a test plan instead of directly reading the requirements and just creating test cases? TERMINATE"
    )

     # Example usage with GPT-3.5
    print("Interaction with GPT-3.5 Agent:")
    gpt3_5_user_proxy.initiate_chat(
        gpt_3_5_assistant,
        message="what are the risks of not testing in software development TERMINATE"
    )

if __name__ == "__main__":
    main()