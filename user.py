import streamlit as st
import mysql.connector
from mysql.connector import Error
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
from hashlib import sha256
import json

class SimpleBlockchain:
    def __init__(self, key=None, iv=None):
        if key and iv:
            self.key = key
            self.iv = iv
        else:
            self.key = get_random_bytes(16)  # AES key for symmetric encryption
            self.iv = get_random_bytes(16)  # Initialization vector
        self.cipher = AES.new(self.key, AES.MODE_CBC, self.iv)  # AES cipher in CBC mode

    def encrypt(self, data):
        padded_data = pad(data.encode(), AES.block_size)
        encrypted_data = self.cipher.encrypt(padded_data)
        return encrypted_data

    def decrypt(self, encrypted_data):
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        decrypted_data = unpad(cipher.decrypt(encrypted_data), AES.block_size)
        return decrypted_data.decode()

    def hash_data(self, data):
        if isinstance(data, bytes):
            return sha256(data).hexdigest()
        else:
            return sha256(data.encode()).hexdigest()

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

def save_user_data(user_data, encrypted_data, data_hash):
    connection = connect_database()
    if connection:
        cursor = connection.cursor()
        try:
            query = """
                INSERT INTO user_details (name, phone_number, email_id, occupation, organization_name, age, 
                    aadhar_number, current_staying_address, work_address, father_name, father_phone_number, mother_name,
                    mother_phone_number, emergency_contact_name, emergency_contact_phone_number, blood_group, gender,
                    encrypted_data, data_hash)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (
                user_data['Name'], user_data.get('Phone Number'), user_data.get('Email ID'), user_data.get('Occupation'),
                user_data.get('Organization Name'), user_data['Age'], user_data.get('Aadhar Number'),
                user_data.get('Current Staying Address'), user_data.get('Work Address'), user_data.get('Father Name'),
                user_data.get('Father Phone Number'), user_data.get('Mother Name'), user_data.get('Mother Phone Number'),
                user_data.get('Emergency Contact Name'), user_data['Emergency Contact Phone Number'], user_data['Blood Group'],
                user_data.get('Gender'), encrypted_data, data_hash
            )
            cursor.execute(query, values)
            connection.commit()
            st.success("User data saved successfully!")
        except Error as e:
            st.error(f"Failed to save data: {e}")
        finally:
            cursor.close()
            connection.close()

def user_page():
    st.title("User Details")
    fields = [
        ("Name", True), ("Phone Number", False), ("Email ID", False), ("Occupation", False),
        ("Organization Name", False), ("Age", True), ("Aadhar Number", False),
        ("Current Staying Address", False), ("Work Address", False), ("Father Name", False),
        ("Father Phone Number", False), ("Mother Name", False), ("Mother Phone Number", False),
        ("Emergency Contact Name", False), ("Emergency Contact Phone Number", True),
        ("Blood Group", True), ("Gender", False)
    ]

    user_data = {field: st.text_input(f"{field}{'*' if is_required else ''}:", help="This field is required" if is_required else None)
                 for field, is_required in fields}

    acknowledge = st.checkbox("I confirm that the details provided are accurate and I accept the terms and conditions.")

    if st.button("Confirm Details and Submit"):
        if all(user_data[field] for field, is_required in fields if is_required and user_data[field]) and acknowledge:
            blockchain = SimpleBlockchain()
            data_str = json.dumps(user_data)
            encrypted_data = blockchain.encrypt(data_str)
            data_hash = blockchain.hash_data(encrypted_data)
            save_user_data(user_data, encrypted_data, data_hash)
            st.success("Data encrypted successfully and saved to database.")
        else:
            st.error("Please fill in all required fields and accept the terms and conditions.")

    if st.button("Go Back to Home"):
        st.session_state.page = 'home'

if __name__ == "__main__":
    user_page()
