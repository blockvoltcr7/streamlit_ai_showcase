import os
from typing import List
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from langchain_community.chat_models import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI


# Load environment variables
load_dotenv()

# Set up API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")

if OPENAI_API_KEY is None:
    raise ValueError("API keys not found. Please set the OPENAI_API_KEY environment variables.")

if GOOGLE_API_KEY not in os.environ:
    os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

gemini_llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-001")
result = gemini_llm.invoke("Write a ballad about LangChain")
print(result)

# Initialize LLMs
llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.7, openai_api_key=OPENAI_API_KEY)

def read_markdown_file(file_path):
    print(f"Reading file: {file_path}")
    with open(file_path, 'r') as file:
        return file.read()

# Read the synthetic requirements document
filepath = os.path.abspath("./data/synthetic_requirements.md")

# Verify the file exists
if not os.path.exists(filepath):
    raise FileNotFoundError(f"File not found: {filepath}")

brd_content = read_markdown_file(filepath)

# Define agents with specific LLMs
product_owner = Agent(
    role='Product Owner',
    goal='Ensure the API meets business needs and create a product backlog',
    backstory='Experienced in financial products with a keen eye for market needs',
    verbose=True,
    allow_delegation=False,
    llm=llm
)

business_analyst = Agent(
    role='Business Analyst',
    goal='Analyze requirements and create detailed functional specifications',
    backstory='Skilled in translating business requirements into technical specifications',
    verbose=True,
    allow_delegation=False,
    llm=llm
)

qa_engineer = Agent(
    role='QA Engineer',
    goal='Develop a comprehensive test plan and test cases',
    backstory='Experienced in API testing and automation with a focus on quality',
    verbose=True,
    allow_delegation=False,
    llm=gemini_llm
)

qa_lead = Agent(
    role='QA Lead',
    goal='Review and approve the test plan. Give feedback to the QA Engineering team',
    backstory='Expert in quality assurance processes and test management',
    verbose=True,
    allow_delegation=False,
    llm=gemini_llm
)

tech_lead = Agent(
    role='Tech Lead',
    goal='Create a technical design document and identify potential technical challenges',
    backstory='Seasoned developer with expertise in API development and financial systems',
    verbose=True,
    allow_delegation=False,
    llm=gemini_llm
)

# Define tasks
task_create_backlog = Task(
    description=f"Review the following Business Requirements Document and create a product backlog. Ensure all requirements are addressed:\n\n{brd_content}",
    agent=product_owner,
    expected_output="A comprehensive product backlog in Markdown format"
)

task_create_func_spec = Task(
    description=f"Using the product backlog and the original requirements, create detailed functional specifications for the Financial Report API. Reference the original requirements:\n\n{brd_content}",
    agent=business_analyst,
    expected_output="Detailed functional specifications document in Markdown format"
)

task_create_tech_design = Task(
    description=f"Based on the functional specifications and the original requirements, create a technical design document for the Financial Report API. Ensure all technical aspects are addressed:\n\n{brd_content}",
    agent=tech_lead,
    expected_output="Comprehensive technical design document in Markdown format"
)

task_create_test_plan = Task(
    description=f"Using the functional specifications, technical design, and the original requirements, create a comprehensive test plan for the Financial Report API. Ensure all testable aspects are covered:\n\n{brd_content}",
    agent=qa_engineer,
    expected_output="Detailed test plan document in Markdown format"
)

task_create_test_strategy = Task(
    description=f"Review the test plan and give feedback on improvements and identify questions to ask to the business to ensure we are covering all the requirements. Identify any risks or missing requirements. Ensure alignment with the original requirements:\n\n{brd_content}",
    agent=qa_lead,
    expected_output="High-level test strategy document in Markdown format"
)

# Create the crew
api_design_crew = Crew(
    agents=[product_owner, business_analyst, qa_engineer, qa_lead, tech_lead],
    tasks=[task_create_backlog, task_create_func_spec, task_create_tech_design, task_create_test_plan, task_create_test_strategy],
    verbose=2,
    process=Process.sequential
)


# Run the crew
result = api_design_crew.kickoff()

# Print the result
print("Crew execution completed. Results:")
print(result)

# Save artifacts
def save_artifact(content, filename):
    directory = "artifacts"
    os.makedirs(directory, exist_ok=True)
    
    # Convert content to string if it's not already
    if not isinstance(content, str):
        content = str(content)
    
    with open(os.path.join(directory, filename), 'w', encoding='utf-8') as file:
        file.write(content)

# Save the overall result
save_artifact(str(result), "crew_execution_result.md")

# Save individual artifacts
artifact_names = ["product_backlog.md", "functional_specifications.md", "technical_design.md", "test_plan.md", "test_strategy.md"]

for task, name in zip(api_design_crew.tasks, artifact_names):
    if hasattr(task, 'output') and task.output:
        save_artifact(task.output, name)
    else:
        print(f"Warning: No output found for task {name}")

print("All artifacts have been saved in the 'artifacts' directory.")

if __name__ == "__main__":
    # You can add any additional setup or execution code here if needed
    pass

result = api_design_crew.kickoff()

# Print the result
print("Crew execution completed. Results:")
print(result)
