import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Set the title of the Streamlit app
st.title("Data Display with Streamlit")

# Create a sample DataFrame
data = {
    "A": np.random.randn(50),
    "B": np.random.randn(50),
    "C": np.random.randn(50)
}
df = pd.DataFrame(data)

# Display a table using Streamlit
st.header("Displaying Tables in Streamlit")
st.table(df.head(10))

# Display the DataFrame in a more interactive format
st.header("Displaying DataFrames in Streamlit")
st.write(df.head(10))

# Create and display a line chart
st.header("Line Chart")
st.line_chart(df)

# Create and display a correlation heatmap
st.header("Correlation Heatmap")
fig, ax = plt.subplots(figsize=(8, 6))
sns.heatmap(df.corr(), annot=True, cmap="coolwarm", ax=ax)
st.pyplot(fig)

# Dynamic Content Example
st.header("Dynamic Content Example")

# Image with caption
st.subheader("Image with Caption")
image_url = "https://streamlit.io/images/brand/streamlit-logo-secondary-colormark-darktext.png"
st.image(image_url, caption="Streamlit Logo")

# Video
st.subheader("Video Example")
video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
st.video(video_url)

# Dynamic text input and display
st.subheader("Dynamic Text Input and Display")
user_input = st.text_input("Enter some text:")
if user_input:
    st.write(f"You entered: {user_input}")

# Dynamic slider and plot
st.subheader("Dynamic Slider and Plot")
x = st.slider('Select a value')
st.write(x, 'squared is', x * x)

# Plotting based on dynamic input
st.subheader("Dynamic Plot")
plot_type = st.selectbox("Choose a plot type", ["Line", "Bar", "Area"])
if plot_type == "Line":
    st.line_chart(df)
elif plot_type == "Bar":
    st.bar_chart(df)
else:
    st.area_chart(df)

# Create and display a bar chart
st.header("Bar Chart")
mean_values = df.mean()
fig, ax = plt.subplots(figsize=(10, 6))
mean_values.plot(kind='bar', ax=ax)
plt.title("Mean Values of A, B, and C")
plt.xlabel("Columns")
plt.ylabel("Mean Value")
st.pyplot(fig)
