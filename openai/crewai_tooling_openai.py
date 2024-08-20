import os
import uuid
import requests
import tiktoken
from crewai import Agent, Task, Crew, Process
from crewai_tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.callbacks import BaseCallbackHandler
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Define the Token Counter Callback
class TokenCounterCallback(BaseCallbackHandler):
    def __init__(self):
        self.token_count = 0
        self.encoding = tiktoken.encoding_for_model("gpt-4o-mini")

    def on_llm_start(self, serialized, prompts, **kwargs):
        for prompt in prompts:
            self.token_count += len(self.encoding.encode(prompt))

    def on_llm_end(self, response, **kwargs):
        for generation in response.generations:
            for output in generation:
                self.token_count += len(self.encoding.encode(output.text))

# Initialize the LLM model
gpt_4o_mini = ChatOpenAI(
    model_name="gpt-4o-mini",
    temperature=0.7,
    callbacks=[TokenCounterCallback()]
)

# Define the Eraser.io API Tool
@tool
def EraserIOTool(prompt: str) -> str:
    """
    Generates a cloud architecture diagram using the Eraser.io API.
    """
    api_key = os.getenv("ERASER_IO_API_KEY")
    if not api_key:
        raise ValueError("ERASER_IO_API_KEY environment variable is not set")

    url = "https://app.eraser.io/api/render/prompt"
    
    payload = {
        "text": prompt,
        "diagramType": "cloud-architecture-diagram",
        "background": True,
        "theme": "dark",
        "scale": "3",
        "returnFile": True
    }

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {api_key}"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()

        output_dir = os.path.join("output", "cloud-architecture-diagram")
        os.makedirs(output_dir, exist_ok=True)

        # Generate a random file name
        random_file_name = f"cloud_arch_diagram_{uuid.uuid4().hex}.png"
        output_path = os.path.join(output_dir, random_file_name)
        
        # Save the image
        with open(output_path, "wb") as f:
            f.write(response.content)
        
        return f"Image saved successfully at: {output_path}"
    
    except requests.RequestException as e:
        return f"Error making request: {e}"
    except IOError as e:
        return f"Error saving file: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"

# Define the Agent
diagram_agent = Agent(
    role='Cloud Architect',
    goal='Generate cloud architecture diagrams based on user prompts',
    backstory=(
        "You are a skilled cloud architect capable of translating complex cloud "
        "infrastructures into clear and detailed diagrams using the Eraser.io API."
    ),
    tools=[EraserIOTool],
    llm=gpt_4o_mini,
    verbose=True
)

# Define the Task
diagram_task = Task(
    description="Generate a cloud architecture diagram for the provided prompt. take the full prompt and pass it into the eraser.io api",
    expected_output="A URL to the generated diagram or a message indicating success.",
    agent=diagram_agent
)

# Form the Crew and kickoff the process
def generate_cloud_diagram(prompt):
    if not prompt.strip():
        return "No prompt provided. Please provide a valid prompt to generate the diagram."

    crew = Crew(
        agents=[diagram_agent],
        tasks=[diagram_task],
        process=Process.sequential
    )
    result = crew.kickoff(inputs={'prompt': prompt})
    return result

# Example usage
if __name__ == "__main__":
    user_prompt = """
    // Define groups and nodes
    Cloud Provider [icon: cloud]
    Kubernetes Cluster [icon: k8s-control-plane] {
      Control Plane {
        API Server [icon: k8s-api]
        Scheduler [icon: k8s-sched]
        Controller Manager [icon: k8s-c-m]
        etcd [icon: k8s-etcd]
      }

      Data Processing {
        Data Ingestion [icon: k8s-node] {
          Raw Data Pod [icon: database]
          ETL Pod [icon: gcp-dataflow]
        }

        Data Storage [icon: k8s-node] {
          Persistent Volume [icon: azure-storage-accounts]
        }
      }

      ML Pipeline [icon: k8s-node] {
        Feature Engineering [icon: gcp-dataprep]
        Model Training [icon: tensorflow]
        Model Evaluation [icon: chart]
        Model Serving [icon: cloud]
      }

      Analytics [icon: k8s-node] {
        Visualization Pod [icon: chart]
        Reporting Pod [icon: file-text]
      }

      API Gateway [icon: k8s-node] {
        Ingress Controller [icon: gcp-cloud-load-balancing]
        Authentication [icon: lock]
      }
    }

    External Services {
      Medical Data Sources [icon: hospital]
      Researchers [icon: users]
      High-Performance Computing [icon: server]
    }

    // Define connections
    Cloud Provider <-> Kubernetes Cluster
    Medical Data Sources --> Data Ingestion
    Data Ingestion --> Data Storage
    Data Storage <--> ML Pipeline
    ML Pipeline --> Analytics
    Analytics --> API Gateway
    API Gateway <--> Researchers
    ML Pipeline <--> High-Performance Computing

    // Set diagram properties
    direction right
    """
    
    diagram_result = generate_cloud_diagram(user_prompt)
    print(f"Generated Diagram Result: {diagram_result}")