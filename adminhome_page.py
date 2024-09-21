import streamlit as st

# Home page
def main():
    st.title("Femguard - Police Portal")

    # Button to navigate to Complaints Page with unique key
    if st.button("Complaints from the User", key="complaints_button"):
        st.session_state.page = "complaints"  # Switch to complaints page

    # Button for user emergency tracking with a unique key
    if st.button("User Emergency Tracking", key="emergency_tracking_button"):
        st.write("Here you can track users in emergency situations.")
        
        # Read from the emergency alert file
        try:
            with open("emergency_alert.txt", "r") as file:
                alert_message = file.read()
                st.warning(alert_message)
        except FileNotFoundError:
            st.info("No current emergency alerts.")
