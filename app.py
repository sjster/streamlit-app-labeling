import streamlit as st

# Set page config
st.set_page_config(
    page_title="Hello World App",
    page_icon="👋",
    layout="centered"
)

# Main content
st.title("Hello World!")
st.write("Welcome to this simple Streamlit application.")

# Add some interactive elements
name = st.text_input("What's your name?", placeholder="Enter your name here")

if name:
    st.success(f"Hello, {name}! 👋")
else:
    st.info("Please enter your name above to get a personalized greeting!")

# Add a button
if st.button("Click me!"):
    st.balloons()
    st.write("🎉 You clicked the button!")
