# chatbot.py
import streamlit as st

def chatbot_page():
    # Always display the main title at the top
    st.title("Femguard")

    # Chatbot Page Content
    st.header("Chatbot Page")
    st.write("This is the chatbot page. Integrate your chatbot functionality here.")

    # Button to go back to the Home Page
    if st.button('Go to Home Page'):
        st.session_state.page = 'home'