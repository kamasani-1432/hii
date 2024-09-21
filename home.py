# home.py
import streamlit as st

def home_page():
    # Create a two-column layout
    col1, col2 = st.columns([9, 1])  # Adjust the ratio to make the button appear on the right

    with col1:
        # Display the main title at the top left
        st.title("Femguard - User page")

    with col2:
        # Create a button at the top right side of the page
        if st.button('My Profile'):
            st.session_state.page = 'user'  # Set session state to navigate to user page

    # Home Page Content
    st.write("Welcome to the Femguard Home Page")

    # Button to go to the Complaint Page
    if st.button('Complaint Page'):
        st.session_state.page = 'complaint'
    
    # Button to go to the Communication Page
    if st.button('Communication'):
        st.session_state.page = 'communication'

    # Button to go to the Chatbot Page
    if st.button('Chatbot'):
        st.session_state.page = 'chatbot'