# This code snippet demonstrates how to call a function to format a template variable instead of using a fixed value.
# You can also pass in functions as template variables instead of fixed values.
# This allows you to dynamically inject certain values, dependent on other values, during query-time.

from llama_index.core import PromptTemplate

# Define a template string with template variables
qa_prompt_tmpl_str = """\
Context information is below.
---------------------
{context_str}
---------------------
Given the context information and not prior knowledge, answer the query.
Query: {query_str}
Answer: \
"""

def format_context_fn(**kwargs):
    # format context with bullet points
    context_list = kwargs["context_str"].split("\n\n")   # split context into list of paragraphs
    fmtted_context = "\n\n".join([f"- {c}" for c in context_list])  # create bullet points from each paragraph
    return fmtted_context

# Create a prompt template with the template var mappings
prompt_tmpl = PromptTemplate(
    qa_prompt_tmpl_str, function_mappings={"context_str": format_context_fn}
)

# Format the prompt template with the context and query strings
context_str = """\
In this work, we develop and release Llama 2, a collection of pretrained and fine-tuned large language models (LLMs) ranging in scale from 7 billion to 70 billion parameters.

Our fine-tuned LLMs, called Llama 2-Chat, are optimized for dialogue use cases.

Our models outperform open-source chat models on most benchmarks we tested, and based on our human evaluations for helpfulness and safety, may be a suitable substitute for closed-source models.
"""

fmt_prompt = prompt_tmpl.format(
    context_str=context_str, query_str="How many params does llama 2 have"
)

print(fmt)