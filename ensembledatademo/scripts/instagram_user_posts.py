import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

root = "https://ensembledata.com/apis"
endpoint = "/instagram/user/posts"
params = {
  "user_id": 18428658,
  "depth": 1,
  "oldest_timestamp": 1666262030,
  "chunk_size": 10,
  "start_cursor": "",
  "alternative_method": False,
  "token": os.getenv("ENSEMBLE_DATA_API")
}

res = requests.get(root+endpoint, params=params)
print(res.json())
