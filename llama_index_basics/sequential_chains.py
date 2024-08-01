"""
This module demonstrates how to create a Simple Chain with a prompt template and an LLM model.
It also shows how to encapsulate prompts into functions for better organization.
"""

import os
from dotenv import load_dotenv
from llama_index.core.query_pipeline import QueryPipeline
from llama_index.core import PromptTemplate
from llama_index.llms.openai import OpenAI

def get_movie_info(movie_name: str) -> str:
    """
    Get information about movies similar to the given movie.

    Args:
        movie_name (str): The name of the movie to find similar movies for.

    Returns:
        str: Information about similar movies.
    """
    prompt_str = "Please give name, cast and year of release for movies similar to the movie {movie_name}"
    prompt_tmpl = PromptTemplate(prompt_str)
    llm = OpenAI(model="gpt-3.5-turbo")

    pipeline = QueryPipeline(chain=[prompt_tmpl, llm], verbose=True)
    return pipeline.run(movie_name=movie_name)

def explain_difference(concept1: str, concept2: str) -> str:
    """
    Explain the difference between two concepts.

    Args:
        concept1 (str): The first concept.
        concept2 (str): The second concept.

    Returns:
        str: An explanation of the difference between the two concepts.
    """
    prompt_str = "Explain the difference between {concept1} and {concept2}"
    prompt_tmpl = PromptTemplate(prompt_str)
    llm = OpenAI(model="gpt-3.5-turbo")

    pipeline = QueryPipeline(chain=[prompt_tmpl, llm], verbose=True)
    return pipeline.run(concept1=concept1, concept2=concept2)

def main():
    """Main function to demonstrate the usage of the defined functions."""
    # Load the OpenAI API Key into the environment variable named OPENAI_API_KEY
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    os.environ["OPENAI_API_KEY"] = api_key

    print("Getting movie info for 'The Matrix':")
    print(get_movie_info("The Matrix"))

    print("\nExplaining the difference between 'discipline' and 'motivation':")
    print(explain_difference("discipline", "motivation"))

if __name__ == "__main__":
    main()
