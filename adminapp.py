import streamlit as st
import home_page  # Updated to correct import if your file is 'homepage.py'
import complaints_page

# Initialize session state for 'page' if it doesn't exist
if "page" not in st.session_state:
    st.session_state.page = "home"  # Set default page to 'home'

# Routing between pages based on session state
if st.session_state.page == "home":
    home_page.main()  # Call the main function from homepage.py
elif st.session_state.page == "complaints":
    complaints_page.complaints_page()  # Call the complaints_page function from complaints_page.py
