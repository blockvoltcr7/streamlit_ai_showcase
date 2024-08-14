import streamlit as st

def main():
    st.title("Streamlit Explanation Features Demo")

    # Sidebar with various explanation features
    with st.sidebar:
        st.header("Model Parameters")

        # 1. Tooltip example
        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            help="Controls randomness: Lowering results in less random completions. As the temperature approaches zero, the model will become deterministic and repetitive."
        )

        # 2. Expander example
        with st.expander("Learn more about Temperature"):
            st.write("""
            Temperature is a hyperparameter that controls the randomness of predictions. 
            It affects the likelihood that the model will produce a particular token.

            - A higher temperature (e.g., 0.8) will produce more diverse outputs.
            - A lower temperature (e.g., 0.2) will produce more focused and deterministic outputs.
            """)

        # 3. Help parameter example
        top_p = st.slider(
            "Top P",
            min_value=0.0,
            max_value=1.0,
            value=0.9,
            help="An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass."
        )

        # 4. Info box example
        st.info("Adjust these parameters to fine-tune the model's output.")

    # Main area
    st.header("Explanation Features Demonstration")
    st.write("This demo showcases different ways to provide explanations and additional information in Streamlit apps.")

    st.subheader("1. Tooltip / Help Text")
    st.write("Hover over or click the '?' icon next to the 'Temperature' slider in the sidebar to see a tooltip explanation.")

    st.subheader("2. Expander")
    st.write("Click on 'Learn more about Temperature' in the sidebar to see an expander with detailed information.")

    st.subheader("3. Help Parameter")
    st.write("The 'Top P' slider in the sidebar also uses the help parameter to provide an explanation.")

    st.subheader("4. Info Box")
    st.write("Notice the info box at the bottom of the sidebar, providing general guidance.")

    # Additional example in main area
    max_tokens = st.number_input(
        "Max Tokens",
        min_value=1,
        max_value=2048,
        value=256,
        help="The maximum number of tokens to generate. Tokens are common sequences of characters found in text."
    )

    # Demonstrating st.info in main area
    st.info("Experiment with these features to enhance the user experience of your Streamlit app!")

if __name__ == "__main__":
    main()