import requests
import os
import uuid
from dotenv import load_dotenv

load_dotenv()

# Fetch the API key from environment variables
api_key = os.getenv("ERASER_IO_API_KEY")
if api_key is None:
    raise ValueError("ERASER_IO_API_KEY environment variable is not set")



url = "https://app.eraser.io/api/render/prompt"



text_body = """
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

payload = {
    "text": text_body,
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
    response.raise_for_status()  # Raise an exception for bad status codes

    #print status code
    print(f"Status code: {response.status_code}")

    # Print the response text
    print("Response:")
    print(response.content)
    
    # Print response headers
    print("Response Headers:")
    print(response.headers)

    # Create the output directory if it doesn't exist
    output_dir = os.path.join("output", "cloud-architecture-diagram")
    os.makedirs(output_dir, exist_ok=True)
    print(f"Output directory: {output_dir}")

    # Generate a random file name
    random_file_name = f"cloud_arch_diagram_{uuid.uuid4().hex}.png"
    output_path = os.path.join(output_dir, random_file_name)
    
    # Save the image
    with open(output_path, "wb") as f:
        f.write(response.content)
    print(f"Image saved successfully at: {output_path}")
except requests.RequestException as e:
    print(f"Error making request: {e}")
except IOError as e:
    print(f"Error saving file: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")