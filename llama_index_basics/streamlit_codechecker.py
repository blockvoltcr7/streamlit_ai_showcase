'''
Create a Stramlit UI that takes in a Coding Question and also the code that the user has written for the question.
The UI should have a button that when clicked should check the code and return the output of the code and
whether the code is correct or not.
'''

import streamlit as st
from llama_index.core import PromptTemplate
from llama_index.core.chat_engine import SimpleChatEngine
from llama_index.llms.gemini import Gemini
from dotenv import load_dotenv
import os

# Load the OpenAI API Key into the environment variable named OPENAI_API_KEY
load_dotenv()   
api_key = os.getenv("GEMINI_API_KEY")
os.environ["GOOGLE_API_KEY"] = api_key

def check_code(code, question, language):

    # Prompt templates
    question_template = """
        You are a Program or Code Checker Assistant. You will have four inputs - the programming question, the code, the language, and the additional input data. 
        You need to check if the provided code is correct to solve the given question and also provide feedback on the code.
        If there in an invalidity in any of the inputs, you are to provide feedback on that as well.
        **Programming Language:** {language}\n\n
        **Coding Question:** {question}\n\n
        **Code:** {code}\n\n
        Question to you as the Code-Checker: Is the provided code correct to solve the given question?
        Output that you must produce: you are to return the output in a well formed JSON object. The JSON object should contain the following:
        - "correct": Y/N (Y if the code is correct, N if the code is incorrect)
        - "feedback": Feedback on the code. This should be a string. If the code is correct, the feedback should be "The code is correct". If the code is incorrect, the feedback should be a string explaining why the code is incorrect.
        - "output": Execute the program and show the output. 
        """
  
    qa_template = PromptTemplate(question_template)

    # you can create text prompt (for completion API)
    prompt = qa_template.format(language=language, question=question, code=code)

    llm = Gemini(model="models/gemini-1.5-pro")
    
    chat_engine = SimpleChatEngine.from_defaults(llm=llm)
    response = chat_engine.chat(prompt)
    
    return response

#-------------->>>

# Build the Streamlit UI

# List of programming languages
languages = ["Python", "Java", "C", "C++", "JavaScript", "TypeScript", "Ruby", "Swift", "Go", "Kotlin", "Rust", "PHP", "C#", "Scala", "Perl", "Objective-C", "R", "Shell", "Groovy", "Lua"]

st.title("Coding Question Checker")

# Dropdown for programming language
language = st.selectbox("Select the Programming Language:", languages)

# Text area for question
question = st.text_area("Enter the Coding Question:", height=5)

# Text area for code
code = st.text_area("Write your code here:", height=50)

# Button to check the code
if st.button("Check Code"):
  if question and code:
    output = check_code(code, question, language)
    st.write("Output:")
    st.code(output)
    

