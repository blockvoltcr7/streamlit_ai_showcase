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
Settings.llm = OpenAI(temperature=0.2, model="gpt-4o-mini")

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





# responses based on llm
# gpt 3.5
# Social media can provide benefits for some youth by offering positive community and connection with others who share identities, abilities, and interests. 
# It can provide access to important information, create a space for self-expression, and help in forming and maintaining friendships online. Social media can 
# also enable diverse peer interactions, offer social support, and provide a platform for positive interactions, especially for marginalized youth. Additionally, 
# it may support mental health and well-being by facilitating peer connections, identity development, and social support.

# gpt4o

# Social media can offer several benefits for children and adolescents, including providing a positive community and connection with others who share similar identities, 
# abilities, and interests. It can also offer access to important information and create a space for self-expression. Social media helps in forming and maintaining friendships online, 
# developing social connections, and having positive interactions with diverse peer groups. This can provide essential social support, especially for marginalized youth, including racial,
#  ethnic, and sexual and gender minorities. Additionally, social media can support mental health and well-being by enabling peer connection, identity development, and social support.
#  Many adolescents report that social media helps them feel more accepted, supported through tough times, allows them to show their creative side, and keeps them connected with their friends' lives.
#  Social media-based mental health interventions may also promote help-seeking behaviors and serve as a gateway to initiating mental health care.

# gpt 4o mini

# Social media can offer several benefits for children and adolescents, including:

# 1. **Community and Connection**: It provides a platform for positive community engagement and connection with others who share similar identities, abilities, and interests.

# 2. **Access to Information**: Social media can serve as a valuable resource for important information and create opportunities for self-expression.

# 3. **Friendship Formation**: It allows youth to form and maintain friendships online, helping them develop social connections.

# 4. **Diverse Interactions**: Online relationships can lead to positive interactions with a more diverse peer group than what is typically available offline, offering essential social support.

# 5. **Support for Marginalized Youth**: For marginalized groups, such as racial, ethnic, and sexual and gender minorities, online social support can be particularly beneficial in buffering against stress.

# 6. **Mental Health Support**: Studies indicate that social media can support the mental health and well-being of LGBTQ+ youth by facilitating peer connections and identity development.

# 7. **Feeling Accepted**: A significant number of adolescents report feeling more accepted and connected to their peers through social media.

# 8. **Creative Expression**: Many young people feel that social media provides a space to showcase their creativity.

# 9. **Help-Seeking Behaviors**: Digital mental health interventions via social media may encourage help-seeking behaviors and serve as a gateway to mental health care for some youth.