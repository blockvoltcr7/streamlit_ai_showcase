import requests
import os
import uuid
from dotenv import load_dotenv

load_dotenv()

##exmaple doc: https://docs.eraser.io/docs/entity-relationship-diagrams


# Fetch the API key from environment variables
api_key = os.getenv("ERASER_IO_API_KEY")
if api_key is None:
    raise ValueError("ERASER_IO_API_KEY environment variable is not set")


url = "https://app.eraser.io/api/render/prompt"

text = """
users [icon: user, color: blue] {
    id string pk
    displayName string
    team_role string
    teams string
}

teams [icon: users, color: blue] {
    id string pk
    name string
}

workspaces [icon: home] {
    id string
    createdAt timestamp
    folderId string
    teamId string
}

folders [icon: folder] {
    id string
    name string
}

chat [icon: message-circle, color: green] {
    duration number
    startedAt timestamp
    endedAt timestamp
    workspaceId string
}

invite [icon: mail, color: green] {
    inviteId string
    type string
    workspaceId string
    inviterId string
}

users.teams <> teams.id
workspaces.folderId > folders.id
workspaces.teamId > teams.id
chat.workspaceId > workspaces.id
invite.workspaceId > workspaces.id
invite.inviterId > users.id
"""

payload = {
    "text": text, 
    "diagramType": "entity-relationship-diagram",
    "background": True,
    "theme": "light",
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
    output_dir = os.path.join("output", "entity-relationship-diagram")
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate a random file name
    random_file_name = f"entity-relationship-diagram{uuid.uuid4().hex}.png"
    output_path = os.path.join(output_dir, random_file_name)
    
    print(f"Image saved successfully at: {output_path}")

except requests.RequestException as e:
    print(f"Error making request: {e}")
except IOError as e:
    print(f"Error saving file: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")