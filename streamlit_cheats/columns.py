import streamlit as st

def main():
    st.title("Streamlit Columns Demo")

    st.header("Two Equal Columns")
    col1, col2 = st.columns(2)
    col1.write('This is Column 1')
    col2.write('This is Column 2')

    st.header("Three Columns with Different Widths")
    col1, col2, col3 = st.columns([3, 1, 1])
    col1.write('This is a wider Column 1')
    col2.write('Column 2')
    col3.write('Column 3')

    st.header("Using 'with' Notation")
    col1, col2 = st.columns(2)
    with col1:
        st.write('This is Column 1 using with notation')
        st.button('Click me!')
    with col2:
        st.write('This is Column 2 using with notation')
        st.checkbox('Check me!')

if __name__ == "__main__":
    main()