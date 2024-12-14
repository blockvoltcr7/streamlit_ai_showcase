import os

import autogen
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def create_config(model="gpt-4o-mini"):
    """Create a configuration for AutoGen agents."""
    return {"model": model, "api_key": os.getenv("OPENAI_API_KEY")}


def create_agent(name, system_message, config):
    """Create an AutoGen agent."""
    return autogen.AssistantAgent(
        name=name, llm_config={"config_list": [config]}, system_message=system_message
    )


def main():
    config = create_config()

    # Create agents
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
        human_input_mode="NEVER",
        max_consecutive_auto_reply=0,
        code_execution_config={
            "use_docker": False
        },  # Disable Docker for code execution
    )

    # Initiate the conversation
    feature_request = "We need a new user registration feature for our web application."

    # Business Analyst creates Jira Story
    human.initiate_chat(business_analyst, message=feature_request)
    ba_response = business_analyst.last_message()["content"]
    print("Business Analyst's Jira Story:")
    print(ba_response)

    # SDET creates Test Plan
    human.initiate_chat(
        sdet,
        message=f"Create an IEEE 829 test plan based on these requirements:\n{ba_response}",
    )
    sdet_response = sdet.last_message()["content"]
    print("\nSDET's Test Plan:")
    print(sdet_response)

    # QE Lead reviews and provides feedback
    human.initiate_chat(
        qe_lead,
        message=f"Review the following Jira Story and Test Plan. Provide feedback and a final assessment.\n\nJira Story:\n{ba_response}\n\nTest Plan:\n{sdet_response}",
    )
    qe_lead_response = qe_lead.last_message()["content"]
    print("\nQE Lead's Feedback and Assessment:")
    print(qe_lead_response)


if __name__ == "__main__":
    main()
