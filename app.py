# app.py
import streamlit as st
from home import home_page
from complaint import complaint_page
from ChatBotWindow import chatbot_page  # Import this from ChatBotWindow.py
from communication import communication_page
from safetystatus import safety_status_page
from user import user_page

st.set_page_config(page_title="Femguard", layout="wide")

if 'page' not in st.session_state:
    st.session_state.page = 'home'

if st.session_state.page == 'home':
    home_page()
elif st.session_state.page == 'complaint':
    complaint_page()
elif st.session_state.page == 'chatbot':
    chatbot_page()  # Use the imported chatbot page here
elif st.session_state.page == 'communication':
    communication_page()
elif st.session_state.page == 'safety_status':
    safety_status_page()
elif st.session_state.page == 'user':
    user_page()
