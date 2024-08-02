import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from llama_index.llms.openai import OpenAI
from llama_index.llms.anthropic import Anthropic
from llama_index.core import Settings

# Load environment variables
load_dotenv()

# Set up API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

if OPENAI_API_KEY is None or ANTHROPIC_API_KEY is None:
    raise ValueError("API keys not found. Please set the OPENAI_API_KEY and ANTHROPIC_API_KEY environment variables.")

# Set up Anthropic tokenizer
anthropic_tokenizer = Anthropic().tokenizer
Settings.tokenizer = anthropic_tokenizer

# Initialize LLMs
openai_llm = OpenAI(model="gpt-4", api_key=OPENAI_API_KEY)
anthropic_llm = Anthropic(model="claude-3-opus-20240229", api_key=ANTHROPIC_API_KEY)

def openai_tool(prompt):
    response = openai_llm.complete(prompt, max_tokens=500)
    return response.text

def anthropic_tool(prompt):
    response = anthropic_llm.complete(prompt)
    return response.text

def read_markdown_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

# Read the synthetic requirements document
brd_content = read_markdown_file("synthetic_requirements.md")

# Define agents with specific LLMs
product_owner = Agent(
    role='Product Owner',
    goal='Ensure the API meets business needs and create a product backlog',
    backstory='Experienced in financial products with a keen eye for market needs',
    verbose=True,
    allow_delegation=False,
    llm=openai_llm
)

business_analyst = Agent(
    role='Business Analyst',
    goal='Analyze requirements and create detailed functional specifications',
    backstory='Skilled in translating business requirements into technical specifications',
    verbose=True,
    allow_delegation=False,
    llm=anthropic_llm
)

qa_engineer = Agent(
    role='QA Engineer',
    goal='Develop a comprehensive test plan and test cases',
    backstory='Experienced in API testing and automation with a focus on quality',
    verbose=True,
    allow_delegation=False,
    llm=openai_llm
)

qa_lead = Agent(
    role='QA Lead',
    goal='Review and approve the test plan, and create a test strategy document',
    backstory='Expert in quality assurance processes and test management',
    verbose=True,
    allow_delegation=False,
    llm=anthropic_llm
)

tech_lead = Agent(
    role='Tech Lead',
    goal='Create a technical design document and identify potential technical challenges',
    backstory='Seasoned developer with expertise in API development and financial systems',
    verbose=True,
    allow_delegation=False,
    llm=openai_llm
)

# Define tasks
task_create_backlog = Task(
    description=f"Review the following Business Requirements Document and create a product backlog. Ensure all requirements are addressed:\n\n{brd_content}",
    agent=product_owner
)

task_create_func_spec = Task(
    description=f"Using the product backlog and the original requirements, create detailed functional specifications for the Financial Report API. Reference the original requirements:\n\n{brd_content}",
    agent=business_analyst
)

task_create_tech_design = Task(
    description=f"Based on the functional specifications and the original requirements, create a technical design document for the Financial Report API. Ensure all technical aspects are addressed:\n\n{brd_content}",
    agent=tech_lead
)

task_create_test_plan = Task(
    description=f"Using the functional specifications, technical design, and the original requirements, create a comprehensive test plan for the Financial Report API. Ensure all testable aspects are covered:\n\n{brd_content}",
    agent=qa_engineer
)

task_create_test_strategy = Task(
    description=f"Review the test plan and create a high-level test strategy document for the Financial Report API project. Ensure alignment with the original requirements:\n\n{brd_content}",
    agent=qa_lead
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
    with open(os.path.join(directory, filename), 'w') as file:
        file.write(content)

save_artifact(result, "crew_execution_result.md")

# Save individual artifacts
artifact_names = ["product_backlog.md", "functional_specifications.md", "technical_design.md", "test_plan.md", "test_strategy.md"]
for task, name in zip(api_design_crew.tasks, artifact_names):
    save_artifact(task.output, name)

print("All artifacts have been saved in the 'artifacts' directory.")

if __name__ == "__main__":
    # You can add any additional setup or execution code here if needed
    pass