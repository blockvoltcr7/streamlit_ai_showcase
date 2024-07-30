# Description: This Code reads the documents from the data folder and then loads the documents into the VectorStoreIndex.
#              The code then queries the index with a question and returns the response.

from llama_index.llms.openai import OpenAI
from llama_index.core import Settings
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core import get_response_synthesizer
from llama_index.core.response_synthesizers import ResponseMode
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.postprocessor import SimilarityPostprocessor
from dotenv import load_dotenv
import os

# Load the OpenAI API Key into the environment variable named OPENAI_API_KEY
load_dotenv()   
api_key = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_API_KEY"] = api_key

# Set the OpenAI model and temperature
# The Settings is a bundle of commonly used resources used during the indexing and querying stage in a 
# LlamaIndex pipeline/application. You can use it to set the global configuration.
Settings.llm = OpenAI(temperature=0.2, model="gpt-3.5-turbo")

# load data using SimpleDirectoryReader
# All files in the data folder are loaded into the index
# each page is a document in the index
documents = SimpleDirectoryReader("./data").load_data()
index = VectorStoreIndex.from_documents(
    documents,
)

# print the number of documents
print(f"Number of documents: {len(documents)}")
print(f"Display a document in the Index: {documents[25].text}")
print("---------------------------------------------")

# configure retriever
# The retriever is used to retrieve the most similar documents to a query
# The similarity_top_k parameter specifies the number of most similar documents to retrieve
retriever = VectorIndexRetriever(
    index=index,
    similarity_top_k=10,
)

# The response synthesizer is used to turn the response data into a human-readable format
response_synthesizer = get_response_synthesizer(response_mode=ResponseMode.COMPACT)

# The query engine is used to query the index and generate a response
# The query engine uses the retriever to retrieve the most similar documents to a query
# The response synthesizer is used to turn the response data into a human-readable format
# The node postprocessors are used to postprocess the nodes in the response data
# The SimilarityPostprocessor filters out nodes with a similarity score below a certain threshold
# The similarity_cutoff parameter specifies the similarity score cutoff

query_engine = RetrieverQueryEngine(
    retriever=retriever,
    node_postprocessors=[SimilarityPostprocessor(similarity_cutoff=0.7, # filter nodes with similarity score below the cutoff 
                                                 filter_empty=True,  # filter empty nodes
                                                 filter_duplicates=True,  # filter duplicate nodes
                                                 filter_similar=True,  # filter similar nodes
                                                 )],
    response_synthesizer=response_synthesizer,                                                 
)

# The query engine is used to query the index and generate a response
# The query engine uses the retriever to retrieve the most similar documents to a query

response = query_engine.query("What are the Potential Benefits of Social Media Use Among Children and Adolescents?") 
print(response)





