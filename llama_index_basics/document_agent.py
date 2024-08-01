from llama_index.llms.openai import OpenAI
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.agent.openai import OpenAIAgent 
from llama_index.core import Settings
from llama_index.core import VectorStoreIndex, ListIndex, SimpleDirectoryReader
from llama_index.core import get_response_synthesizer
from llama_index.core.query_engine import RetrieverQueryEngine
from dotenv import load_dotenv
from llama_index.core.response_synthesizers import ResponseMode
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core import get_response_synthesizer
from llama_index.llms.gemini import Gemini
from llama_index.core import Settings
import os

# Load the OpenAI API Key into the environment variable named OPENAI_API_KEY
load_dotenv()   
api_key = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_API_KEY"] = api_key

# Set up model configuration
Settings.llm = OpenAI(temperature=0.5,
    model="gpt-3.5-turbo") 


# Load 3 PDF documents on mental Haalth from the folder, using SimpleDirectoryReader

titles = [
    "drake_kendrick_beef", 
    "drake", 
    "kendrick"
    ]

documents = {}
for title in titles:
    documents[title] = SimpleDirectoryReader(input_files=[f"data/drake_beef/{title}.pdf"]).load_data()
print(f"loaded documents with {len(documents)} documents")

# documents = SimpleDirectoryReader(documents).load_data()
# index = VectorStoreIndex.from_documents(documents)

# query_engine = index.as_query_engine()

# # Ask a question
# response = query_engine.query("why did drake and kendrick beef?")
# print(response)

# Iteratively, build three Tools - one for each document, with theirr corresponding retreiver objects

query_engine_tools = []
response_synthesizer = get_response_synthesizer(response_mode=ResponseMode.COMPACT)
for title in titles:

    # build vector index
    vector_index = VectorStoreIndex.from_documents(documents[title])
    retriever = VectorIndexRetriever(index=vector_index, similarity_top_k=3)
    # define query engines
    query_engine = RetrieverQueryEngine(
        retriever=retriever,
        node_postprocessors=[SimilarityPostprocessor(similarity_cutoff=0.7, # filter nodes with similarity score below the cutoff 
                                                    filter_empty=True,  # filter empty nodes
                                                    filter_duplicates=True,  # filter duplicate nodes
                                                    filter_similar=True,  # filter similar nodes
                                                    )],
        response_synthesizer=response_synthesizer,                                                 
    )

    # define tools for each document 
    query_engine_tools += [
        QueryEngineTool(
            query_engine=query_engine,
            metadata=ToolMetadata(
                name=f"vector_tool_{title}",
                description=f"Useful for retrieving specific context related to {title}"
            ),
        )
        ] 

# build agent
agent = OpenAIAgent.from_tools(
    query_engine_tools,
    verbose=True,
)

# print the agent and the number, names of tools
print("Agent: ", agent)
print("Number of Tools: ", len(query_engine_tools))
print("Tool Names: ", [tool.metadata.name for tool in query_engine_tools])

# agent.query("what was Kendrick lamar stage name?")

# agent.query("at what age did Drake start acting? what tv show did he star in?")

agent.query("tell me about J.cole collab with kendrick").response