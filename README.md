# AI Model Showcase with Streamlit

This project is a comprehensive collection of experiments and demonstrations using various AI models, showcased through Streamlit applications. It serves as a playground for exploring different AI technologies and their applications.

## Project Overview

This repository contains multiple Python scripts that demonstrate the use of various AI models and libraries, including:

- OpenAI's GPT models
- Google's Gemini
- Anthropic's Claude
- Mistral AI
- Groq
- LlamaIndex
- Langchain

The project uses Streamlit to create interactive web applications that showcase these AI models' capabilities.

## Key Features

1. **Multi-Model Chat Interfaces**: Implementations of chat-based applications using different AI providers (OpenAI, Claude AI, Together AI).
   ```python:basics/chat_open_source.py
   startLine: 1
   endLine: 40
   ```

2. **Image Processing with AI**: Demonstrations of AI-powered image analysis and processing.
   ```python:gemini_google_basics/gemini_vision_pro.py
   startLine: 1
   endLine: 25
   ```

3. **Financial Analysis**: AI-powered financial data analysis and visualization.
   ```python:groq/groq_finance_exmaple_streamlit.py
   startLine: 1
   endLine: 14
   ```

4. **Document Analysis**: AI-powered document processing and analysis using LlamaIndex.
   ```python:llama_index_basics/document_agent.py
   startLine: 1
   endLine: 35
   ```

5. **Streamlit UI Enhancements**: Various Streamlit UI improvements and custom components.
   ```python:streamlit_cheats/1.34/background-colors/0_🎨_About.py
   startLine: 1
   endLine: 51
   ```

6. **Progress Tracking**: Implementation of progress bars in Streamlit applications.
   ```python:streamlit_cheats/streamlit_stqdm_demo.py
   startLine: 1
   endLine: 45
   ```

## Getting Started

1. Clone this repository.
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up the necessary API keys for the AI services you want to use (OpenAI, Google, Anthropic, etc.).
4. Run the desired Streamlit application:
   ```
   streamlit run [script_name].py
   ```

## Project Structure

- `basics/`: Contains basic implementations and examples.
- `gemini_google_basics/`: Google Gemini model implementations.
- `groq/`: Groq model implementations.
- `llama_index_basics/`: LlamaIndex implementations.
- `nvidia_nims/`: NVIDIA NeMo implementations.
- `streamlit_cheats/`: Streamlit UI enhancements and examples.

## Contributing

Contributions to this project are welcome! Please feel free to submit a Pull Request.

## License

[Specify your license here]

## Acknowledgements

This project uses various AI models and libraries. Please refer to their respective licenses and terms of use.
