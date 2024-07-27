import streamlit as st
import numpy as np

def main():
    st.title("Streamlit Chat Demo")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            if message["role"] == "assistant":
                st.line_chart(np.random.randn(30, 3))

    # Chat input
    prompt = st.chat_input("Say something")
    if prompt:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
        
        # Simulate assistant response
        with st.chat_message("assistant"):
            response = f"Echo: {prompt}"
            st.write(response)
            st.line_chart(np.random.randn(30, 3))
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Rerun the script to update the chat history display
        st.rerun()

if __name__ == "__main__":
    main()