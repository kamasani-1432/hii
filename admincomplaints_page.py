import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

# Configure database connection (replace with your own credentials)
DATABASE_URL = "mysql+pymysql://root:Ha%40201105@localhost:3306/femguard"
engine = create_engine(DATABASE_URL)

# Function to load data from the database
def load_complaints():
    query = "SELECT * FROM complaint"  # Adjust to match your table
    with engine.connect() as connection:
        data = pd.read_sql(query, connection)
    return data

# Complaints page
def complaints_page():
    st.title("Complaints from Users")

    # Fetch complaints data from database
    complaints_data = load_complaints()

    # Display the data as a table
    st.table(complaints_data)

    # Button to go back to the home page
    if st.button("Go Back"):
        st.session_state.page = "home"  # Switch back to home page
