# Streamlit Web Application Overview

This Streamlit Python file creates a simple web application with interactive elements to demonstrate session state management, navigation between different pages, and the use of various widgets. Here's a breakdown of its functionality:

## Session State Initialization
At the beginning, it checks if a `counter` variable exists in the session state. If not, it initializes `st.session_state.counter` to `0`. This is used to persist data (like a counter value) across user sessions and page reloads.

## Increment Counter Function
Defines a function `increment_counter()` that increments the `counter` variable in the session state by `1`. This function demonstrates how to modify session state.

## Page Navigation
Uses a radio button (`st.radio`) to allow the user to select between three pages: "Home", "About", and "Contact". Based on the selection, different content is displayed:

### Home Page
- Displays the current value of the counter and includes a button ("Increment Counter") that, when clicked, calls the `increment_counter()` function to increment the counter.
- Welcomes the user to the home page and displays additional widgets:
  - A slider to select a value between `0` and `100`, with a default value of `50`.
  - A dropdown select box to choose between three options: "Option 1: Cats", "Option 2: Dogs", and "Option 3: Birds".
  - A date input widget to select a date.
- The selected values from the slider, dropdown, and date input are displayed below the widgets.

### About Page
- Displays a simple message, "This is the about section".

### Contact Page
- Displays a message, "Feel free to contact us", indicating a section where contact information could be provided.

Overall, this file showcases basic Streamlit features for creating interactive web applications, including session state management, conditional rendering based on user input, and the use of various input widgets to collect and display user input.