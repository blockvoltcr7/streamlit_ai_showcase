import os  # Importing the os module to interact with the operating system

import autogen  # Importing the autogen module for creating AutoGen agents
import streamlit as st  # Importing streamlit for building the web application interface
from dotenv import (
    load_dotenv,
)  # Importing load_dotenv to load environment variables from a .env file

# Load environment variables from the .env file
load_dotenv()


def create_config(model="gpt-4o-mini"):
    """
    Create a configuration for AutoGen agents.

    Args:
        model (str): The model to be used for the AutoGen agent. Default is "gpt-4o-mini".

    Returns:
        dict: A dictionary containing the model configuration, including the model name and API key.
    """
    return {"model": model, "api_key": os.getenv("OPENAI_API_KEY")}


def create_agent(name, system_message, config):
    """
    Create an AutoGen agent.

    Args:
        name (str): The name of the agent.
        system_message (str): The system message that defines the agent's role.
        config (dict): The configuration dictionary for the agent, including model and API key.

    Returns:
        AssistantAgent: An instance of the AutoGen AssistantAgent.
    """
    return autogen.AssistantAgent(
        name=name, llm_config={"config_list": [config]}, system_message=system_message
    )


def main():
    """
    Main function to run the Streamlit application for the AutoGen SDLC Workflow.

    This function sets up the user interface, collects user input for feature requests,
    and manages the interaction between different AutoGen agents (Business Analyst, SDET, QE Lead).
    """
    st.title("AutoGen SDLC Workflow")  # Set the title of the Streamlit app

    # Get user input for the feature request
    feature_request = st.text_input(
        "Enter the feature request:",
        "We need a new user registration feature for our web application.",
    )

    if st.button("Submit"):  # Check if the submit button is pressed
        config = create_config()  # Create the configuration for the agents

        # Create agents with specific roles and system messages
        business_analyst = create_agent(
            "Business_Analyst",
            "You are a Business Analyst. Create requirements for new features in the format of a Jira Story, including a high-level description, acceptance criteria, and sample test data.",
            config,
        )

        sdet = create_agent(
            "SDET",
            "You are a Software Developer in Test (SDET) with strong automation skills. Create an IEEE 829 test plan based on the requirements provided by the Business Analyst.",
            config,
        )

        qe_lead = create_agent(
            "QE_Lead",
            "You are a QE Lead. Review the requirements from the Business Analyst and the test plan from the SDET. Provide feedback and a final assessment.",
            config,
        )

        # Create a Human agent to initiate the conversation
        human = autogen.UserProxyAgent(
            name="Human",
            human_input_mode="NEVER",  # Set to NEVER to prevent human input during the conversation
            max_consecutive_auto_reply=0,  # Limit the number of consecutive auto replies
            code_execution_config={
                "use_docker": False  # Disable Docker for code execution
            },
        )

        # Initiate the conversation with the Business Analyst
        human.initiate_chat(business_analyst, message=feature_request)
        ba_response = business_analyst.last_message()[
            "content"
        ]  # Get the response from the Business Analyst
        st.subheader(
            "Business Analyst's Jira Story:"
        )  # Display the subheader for the response
        st.write(ba_response)  # Write the response to the Streamlit app

        # Initiate the chat with the SDET for creating the test plan
        human.initiate_chat(
            sdet,
            message=f"Create an IEEE 829 test plan based on these requirements:\n{ba_response}",
        )
        sdet_response = sdet.last_message()["content"]  # Get the response from the SDET
        st.subheader("SDET's Test Plan:")  # Display the subheader for the response
        st.write(sdet_response)  # Write the response to the Streamlit app

        # Initiate the chat with the QE Lead for feedback and assessment
        human.initiate_chat(
            qe_lead,
            message=f"Review the following Jira Story and Test Plan. Provide feedback and a final assessment.\n\nJira Story:\n{ba_response}\n\nTest Plan:\n{sdet_response}",
        )
        qe_lead_response = qe_lead.last_message()[
            "content"
        ]  # Get the response from the QE Lead
        st.subheader(
            "QE Lead's Feedback and Assessment:"
        )  # Display the subheader for the response
        st.write(qe_lead_response)  # Write the response to the Streamlit app


if __name__ == "__main__":
    main()  # Execute the main function when the script is run
