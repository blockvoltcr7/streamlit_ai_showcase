import streamlit as st
from streamlit_extras.add_vertical_space import add_vertical_space

st.write("Let's add some vertical space!")

add_vertical_space(3)
st.write("3 units of vertical space were just added.")

add_vertical_space(height=50)
st.write("50 pixels of vertical space were just added.")

add_vertical_space(height="5rem")
st.write("5rem of vertical space were just added.")
