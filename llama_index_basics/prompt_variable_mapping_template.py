# This script demonstrates how to use template var mappings to map the expected prompt keys to the keys in your template.
# Template var mappings allow you to specify a mapping from the "expected" prompt keys 
# (e.g. context_str and query_str for response synthesis), with the keys actually in your template.

from llama_index.core import PromptTemplate

my_context = ""
my_query = ""

# Define a template string with template variables
qa_prompt_tmpl_str = """\
Context information is below.
---------------------
{my_context}
---------------------
Given the context information and not prior knowledge, answer the query.
Query: {my_query}
Answer: \
"""

template_var_mappings = {"context_str": "my_context", "query_str": "my_query"}

# Create a prompt template with the template var mappings
prompt_tmpl = PromptTemplate(
    qa_prompt_tmpl_str, template_var_mappings=template_var_mappings
)

# Format the prompt template with the context and query strings
fmt_prompt = prompt_tmpl.format(
    context_str="In this work, we develop and release Llama 2, a collection of pretrained and fine-tuned large language models (LLMs) ranging in scale from 7 billion to 70 billion parameters",
    query_str="How many params does llama 2 have"
)
print(fmt_prompt)