import autogen
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def create_config(model="gpt-4-0613"):
    """Create a configuration for AutoGen agents."""
    return {
        "model": model,
        "api_key": os.getenv("OPENAI_API_KEY")
    }

def create_agent(name, system_message, config):
    """Create an AutoGen agent."""
    return autogen.AssistantAgent(
        name=name,
        llm_config={"config_list": [config]},
        system_message=system_message
    )

def main():
    config = create_config()

    # Create agents
    business_analyst = create_agent(
        "Business_Analyst",
        "You are a Business Analyst. Create requirements for new features in the format of a Jira Story, including a high-level description, acceptance criteria, and sample test data.",
        config
    )

    sdet = create_agent(
        "SDET",
        "You are a Software Developer in Test (SDET) with strong automation skills. Create an IEEE 829 test plan based on the requirements provided by the Business Analyst.",
        config
    )

    qe_lead = create_agent(
        "QE_Lead",
        "You are a QE Lead. Review the requirements from the Business Analyst and the test plan from the SDET. Provide feedback and a final assessment.",
        config
    )

    # Initiate the conversation
    feature_request = "We need a new user registration feature for our web application."

    # Business Analyst creates requirements
    ba_response = business_analyst.generate_response(
        [{"role": "user", "content": f"Create a Jira Story for this feature request: {feature_request}"}]
    )
    print("Business Analyst's Jira Story:")
    print(ba_response)

    # SDET creates test plan
    sdet_response = sdet.generate_response(
        [{"role": "user", "content": f"Create an IEEE 829 test plan based on these requirements:\n{ba_response}"}]
    )
    print("\nSDET's Test Plan:")
    print(sdet_response)

    # QE Lead reviews and provides feedback
    qe_lead_response = qe_lead.generate_response([
        {"role": "user", "content": f"Review the following Jira Story and Test Plan. Provide feedback and a final assessment.\n\nJira Story:\n{ba_response}\n\nTest Plan:\n{sdet_response}"}
    ])
    print("\nQE Lead's Feedback and Assessment:")
    print(qe_lead_response)

if __name__ == "__main__":
    main()