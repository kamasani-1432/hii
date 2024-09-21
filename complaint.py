import streamlit as st
import mysql.connector
from mysql.connector import Error
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
from hashlib import sha256
from datetime import datetime
import os

# Function to connect to the database
def connect_database():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Ha@201105',
            database='femguard'
        )
        return connection
    except Error as e:
        st.error(f"Database connection failed: {e}")
        return None

# Function to save complaint data with both encrypted and decrypted remarks
def save_complaint_data(date_incident, time_incident, stage, remarks_encrypted, remarks_hash, remarks_decrypted, file_path=None):
    connection = connect_database()
    if connection:
        cursor = connection.cursor()
        try:
            query = """
                INSERT INTO complaint (date_incident, time_incident, severity_stage, remarks_encrypted, remarks_hash, remarks_decrypted, file_path)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            values = (date_incident, time_incident, stage, remarks_encrypted, remarks_hash, remarks_decrypted, file_path)
            cursor.execute(query, values)
            connection.commit()
            st.success("Complaint registered successfully and saved to the database!")
        except Error as e:
            st.error(f"Failed to save complaint: {e}")
        finally:
            cursor.close()
            connection.close()

# Complaint page implementation
def complaint_page():
    # Function to save uploaded file
    def save_uploadedfile(uploadedfile):
        if not os.path.exists('uploaded_files'):
            os.makedirs('uploaded_files')
        file_path = os.path.join("uploaded_files", uploadedfile.name)
        with open(file_path, "wb") as f:
            f.write(uploadedfile.getbuffer())
        return file_path

    # SimpleBlockchain class for encryption and decryption
    class SimpleBlockchain:
        def __init__(self):
            self.key = get_random_bytes(16)  # AES key for symmetric encryption
            self.iv = get_random_bytes(16)   # Initialization vector
            self.cipher = AES.new(self.key, AES.MODE_CBC, self.iv)  # AES cipher in CBC mode

        def encrypt(self, data):
            # Encrypts the data
            padded_data = pad(data.encode(), AES.block_size)
            cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
            encrypted_data = cipher.encrypt(padded_data)
            return encrypted_data

        def decrypt(self, encrypted_data):
            # Decrypts the data
            cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
            decrypted_data = unpad(cipher.decrypt(encrypted_data), AES.block_size)
            return decrypted_data.decode()

        def hash_data(self, data):
            # Creates a SHA-256 hash of the data
            return sha256(data).hexdigest()

    # Display main title at the top
    st.title("Femguard")

    # Complaint Page Content
    st.header("Complaint Page")
    st.write("This is the complaint page. Fill out the form to register a complaint.")

    # Initialize the SimpleBlockchain object
    blockchain = SimpleBlockchain()

    # Form for submitting a complaint
    with st.form(key='complaint_form'):
        # Collecting date of the incident
        date_incident = st.date_input("Date of Incident:", datetime.now())

        # Collecting time of the incident
        time_incident = st.time_input("Time of Incident:", datetime.now().time())
        
        # Severity of the incident with descriptions
        stage = st.radio("Severity of Incident:", 
                         options=[
                             'Stage 1: Objectification',
                             'Stage 2: Glass Ceiling',
                             'Stage 3: Harassment, Threats, Verbal Abuse',
                             'Stage 4: Physical and Emotional Abuse, Rape, Sexual Assault'
                         ], 
                         help="Select the stage that best describes the severity of the incident.")
        
        # User input for remarks
        remarks = st.text_area("Remarks of the Incident:")
        
        # File upload for proof
        uploaded_file = st.file_uploader("Upload Proof (optional):", type=['pdf', 'docx', 'txt', 'jpg', 'jpeg', 'png', 'gif'])
        
        # Encrypt the complaint details
        encrypted_remarks = blockchain.encrypt(remarks) if remarks else None
        remarks_hash = blockchain.hash_data(encrypted_remarks) if encrypted_remarks else None
        decrypted_remarks = remarks  # Save the original, unencrypted remarks
        
        # Submit button
        submit_button = st.form_submit_button("Register Complaint")
    
    # Processing after form submission
    if submit_button:
        # If the user uploaded a file, save it
        file_path = None
        if uploaded_file is not None:
            file_path = save_uploadedfile(uploaded_file)
        
        # Ensure remarks are entered
        if encrypted_remarks:
            # Save the encrypted and decrypted remarks along with other details to the database
            save_complaint_data(date_incident, time_incident, stage, encrypted_remarks.hex(), remarks_hash, decrypted_remarks, file_path)
        else:
            st.error("Please provide remarks to register a complaint.")
        
    # Button to go back to the Home Page
    if st.button('Go to Home Page'):
        st.session_state.page = 'home'
