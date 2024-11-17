import json
import logging
import os
import time
from datetime import datetime

import streamlit as st
import tiktoken
from anthropic import AI_PROMPT, HUMAN_PROMPT, Anthropic
from streamlit_float import float_init

from openai import OpenAI

# Set up logging
logging.basicConfig(encoding="UTF-8", level=logging.INFO)
logger = logging.getLogger(__name__)

# Page config with custom theme
st.set_page_config(
    page_title="Enhanced AI Chat Interface", page_icon="🤖", layout="wide"
)

# Custom CSS for styling
st.markdown(
    """
<style>
    /* Main container styling */
    .main {
        padding: 2rem;
    }
    
    /* Chat message styling */
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        animation: fadeIn 0.5s ease-in;
    }
    
    .user-message {
        background-color: rgba(70, 130, 180, 0.1);
        border-left: 4px solid steelblue;
    }
    
    .assistant-message {
        background-color: rgba(60, 179, 113, 0.1);
        border-left: 4px solid mediumseagreen;
    }
    
    /* Animation keyframes */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Floating button styling */
    .floating-button {
        position: fixed;
        bottom: 20px;
        right: 20px;
        padding: 10px 20px;
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
        cursor: pointer;
        z-index: 1000;
    }
    
    /* Model selection styling */
    .model-select {
        margin-bottom: 1rem;
    }
    
    /* Token counter styling */
    .token-counter {
        font-size: 0.8rem;
        color: #666;
        text-align: right;
    }
    
    /* Custom sidebar styling */
    .sidebar .sidebar-content {
        background-color: #f5f5f5;
    }
</style>
""",
    unsafe_allow_html=True,
)


class ChatInterface:
    def __init__(self):
        self.init_session_state()
        self.setup_sidebar()

    def init_session_state(self):
        """Initialize session state variables"""
        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "conversation_history" not in st.session_state:
            st.session_state.conversation_history = []
        if "model_provider" not in st.session_state:
            st.session_state.model_provider = "OpenAI"
        if "selected_model" not in st.session_state:
            st.session_state.selected_model = "gpt-4o-mini"  # Default model

    def setup_sidebar(self):
        """Set up the sidebar with model selection and settings"""
        with st.sidebar:
            st.title("Chat Settings")

            # Model provider selection
            st.session_state.model_provider = st.selectbox(
                "Select AI Provider:",
                ["OpenAI", "Claude AI"],
                key="model_select",
            )

            # Model-specific dropdown based on provider
            if st.session_state.model_provider == "OpenAI":
                st.session_state.selected_model = st.selectbox(
                    "Select Model:",
                    ["gpt-4o-mini", "gpt-4o"],
                    key="openai_model_select",
                )
            else:  # Claude AI
                st.session_state.selected_model = st.selectbox(
                    "Select Model:",
                    [
                        "claude-3-5-sonnet-20241022",
                        "claude-3-5-haiku-20241022",
                        "claude-3-opus-20240229",
                    ],
                    key="claude_model_select",
                )

            # Model-specific settings
            self.temperature = st.slider("Temperature", 0.0, 1.0, 0.7)
            self.max_tokens = st.slider("Max Tokens", 100, 2000, 500)

            # Chat history options
            if st.button("Clear Chat History"):
                st.session_state.messages = []
                st.session_state.conversation_history = []
                st.success("Chat history cleared!")

            # Export options
            if st.button("Export Chat History"):
                self.export_chat_history()

            # Display token usage
            if st.session_state.messages:
                self.display_token_usage()

    def get_client(self):
        """Initialize and return the appropriate client based on selected provider"""
        if st.session_state.model_provider == "OpenAI":
            return (
                OpenAI(api_key=os.getenv("OPENAI_API_KEY")),
                st.session_state.selected_model,
            )
        elif st.session_state.model_provider == "Claude AI":
            return (
                Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY")),
                st.session_state.selected_model,
            )

    def display_token_usage(self):
        """Display token usage statistics"""
        enc = tiktoken.get_encoding("cl100k_base")
        total_tokens = sum(
            len(enc.encode(msg["content"])) for msg in st.session_state.messages
        )
        st.sidebar.markdown(f"**Total Tokens Used:** {total_tokens}")

    def export_chat_history(self):
        """Export chat history to JSON file"""
        if not st.session_state.messages:
            st.sidebar.warning("No chat history to export!")
            return

        export_data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "model_provider": st.session_state.model_provider,
            "messages": st.session_state.messages,
        }

        # Create download button
        st.sidebar.download_button(
            label="Download Chat History",
            data=json.dumps(export_data, indent=2),
            file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
        )

    def handle_user_input(self, prompt):
        """Process user input and generate response"""
        if not prompt:
            return

        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get client and model
        client, model = self.get_client()

        # Generate response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""

            try:
                if st.session_state.model_provider in ["OpenAI"]:
                    for response in client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": m["role"], "content": m["content"]}
                            for m in st.session_state.messages
                        ],
                        stream=True,
                        temperature=self.temperature,
                        max_tokens=self.max_tokens,
                    ):
                        full_response += response.choices[0].delta.content or ""
                        message_placeholder.markdown(full_response + "▌")

                elif st.session_state.model_provider == "Claude AI":
                    prompt = self.format_claude_prompt()
                    stream = client.completions.create(
                        model=model,
                        prompt=prompt,
                        max_tokens_to_sample=self.max_tokens,
                        stream=True,
                        temperature=self.temperature,
                    )
                    for completion in stream:
                        full_response += completion.completion or ""
                        message_placeholder.markdown(full_response + "▌")

                message_placeholder.markdown(full_response)
                st.session_state.messages.append(
                    {"role": "assistant", "content": full_response}
                )

            except Exception as e:
                logger.error(f"Error generating response: {str(e)}")
                st.error(f"An error occurred: {str(e)}")

    def format_claude_prompt(self):
        """Format the prompt for Claude AI"""
        prompt = ""
        for m in st.session_state.messages:
            if m["role"] == "user":
                prompt += f"{HUMAN_PROMPT} {m['content']}"
            else:
                prompt += f"{AI_PROMPT} {m['content']}"
        return (
            prompt
            + f"{HUMAN_PROMPT} {st.session_state.messages[-1]['content']}{AI_PROMPT}"
        )

    def run(self):
        """Main method to run the chat interface"""
        st.title("🤖 AI Chat Interface")

        # Initialize floating UI elements
        float_init()

        # Display chat messages from history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Chat input
        if prompt := st.chat_input("Send a message...", key="chat_input"):
            self.handle_user_input(prompt)


if __name__ == "__main__":
    chat_interface = ChatInterface()
    chat_interface.run()
