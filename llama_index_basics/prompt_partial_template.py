from llama_index.core import PromptTemplate

# Define a prompt template string with three placeholder variables  
qa_prompt_tmpl_str = """\
Context information is below.
---------------------
{context_str}
---------------------
Given the context information and not prior knowledge, answer the query.
Please write the answer in the style of {tone_name}
Query: {query_str}
Answer: \
"""

prompt_tmpl = PromptTemplate(qa_prompt_tmpl_str)

# Partially format the prompt template with the tone_name variable
partial_prompt_tmpl = prompt_tmpl.partial_format(tone_name="Shakespeare")

# Print the partially formatted prompt template
fmt_prompt = partial_prompt_tmpl.format(
    context_str="In this work, we develop and release Llama 2, a collection of pretrained and fine-tuned large language models (LLMs) ranging in scale from 7 billion to 70 billion parameters",
    query_str="How many params does llama 2 have",
)
print(fmt_prompt)

