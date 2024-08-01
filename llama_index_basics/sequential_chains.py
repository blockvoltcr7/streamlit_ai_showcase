# This code demonstrates how to create a Simple Chain with a prompt template and an LLM model.

from llama_index.core.query_pipeline import QueryPipeline
from llama_index.core import PromptTemplate
from llama_index.llms.openai import OpenAI
import os
from dotenv import load_dotenv

# Load the OpenAI API Key into the environment variable named OPENAI_API_KEY
load_dotenv()   
api_key = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_API_KEY"] = api_key

# try chaining basic prompts
prompt_str = "Please give name, cast and year of release for movies similar to the movie {movie_name}"
prompt_tmpl = PromptTemplate(prompt_str)
llm = OpenAI(model="gpt-3.5-turbo")

# define query pipeline with the prompt template and the LLM model
p = QueryPipeline(chain=[prompt_tmpl, llm], verbose=True)

# run the pipeline
response = p.run(movie_name="The Matrix")

print(response)
prompt_str = "explain the difference between {discipline} and {motivation}"
prompt_tmpl = PromptTemplate(prompt_str)

pipeline = QueryPipeline(chain=[prompt_tmpl, llm], verbose=True)

print(pipeline.run(discipline="discipline",motivation="motivation"))