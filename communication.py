import streamlit as st
import requests
from twilio.rest import Client
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import joblib
import pandas as pd
import numpy as np
import random

# Convert all float32 values to float64
def convert_to_float64(data):
    return np.array(data, dtype=np.float64)

# Function to create the heatmap based on predicted risk levels
def plot_risk_map(locations):
    center_lat, center_lon = 13.0827, 80.2707
    m = folium.Map(
        location=[center_lat, center_lon], 
        zoom_start=12
    )

    # Ensure all risk values are float64 to avoid serialization issues
    heat_data = [[lat, lon, convert_to_float64(risk)] for lat, lon, risk in locations]
    
    HeatMap(heat_data, min_opacity=0.5, max_val=1, radius=20, blur=15, 
            gradient={0.4: 'green', 0.7: 'orange', 1: 'red'}).add_to(m)

    return m

# Fallback encoding function to handle unseen labels
def encode_with_fallback(value, encoder):
    """
    Encodes the given value using the provided encoder.
    If the value is not seen by the encoder, the first class of the encoder is used as a fallback.
    """
    try:
        return encoder.transform([value])[0]
    except ValueError:
        st.warning(f"Unseen label '{value}' encountered. Using default value.")
        return encoder.transform([encoder.classes_[0]])[0]

# Predict risk status using the model with encoding logic and unseen labels handling
def predict_risk_levels(locations):
    # Load model and encoders
    model = joblib.load('models/xgb_classifier_model.pkl')
    encoders = joblib.load('models/label_encoders.pkl')

    risk_levels = []
    for location in locations:
        lat, lon, location_name = location
        input_data = {
            'Location': location_name,
            'Latitude': lat,
            'Longitude': lon,
            'Time_of_Day': 'Morning',  # Example time of day, modify as needed
            'Weather_Conditions': 'Clear',  # Example weather condition
            'Population_Density': 'Medium',  # Example population density
            'Nearby_Facilities': 5,  # Example nearby facilities count
            'Age_Group': 'Adult'  # Example age group
        }

        # Apply encoders to input data, handle unseen labels by setting a default value
        input_data['Location'] = encode_with_fallback(input_data['Location'], encoders['Location'])
        input_data['Time_of_Day'] = encode_with_fallback(input_data['Time_of_Day'], encoders['Time_of_Day'])
        input_data['Weather_Conditions'] = encode_with_fallback(input_data['Weather_Conditions'], encoders['Weather_Conditions'])
        input_data['Population_Density'] = encode_with_fallback(input_data['Population_Density'], encoders['Population_Density'])
        input_data['Age_Group'] = encode_with_fallback(input_data['Age_Group'], encoders['Age_Group'])

        input_df = pd.DataFrame([input_data])

        # Get probability of 'Unsafe' from the model
        probabilities = model.predict_proba(input_df)[0]
        risk_factor = probabilities[1]  # Using 'Unsafe' probability as risk factor

        # Append location with predicted risk factor
        risk_levels.append((lat, lon, risk_factor))

    return risk_levels

def communication_page():
    # Twilio setup
    account_sid = 'ACef646e3875aadd1e0c5d08676f49de77'
    auth_token = '8a769912087a64c8fa0db126b7ac1228'
    twilio_number = '+12083579769'
    to_number = '+919176274608'

    client = Client(account_sid, auth_token)

    def send_location_sms():
        location_link = "https://maps.app.goo.gl/CZj1QCrL8Uy6ZB5g8"
        message_body = f"Your contact is traveling in a danger zone. Track their location here: {location_link}"
        
        try:
            # Sending SMS using Twilio client
            message = client.messages.create(
                body=message_body,
                from_=twilio_number,
                to=to_number
            )
            st.success(f"SMS sent: {message.sid}")
            
            # Write to the emergency alert file
            with open("emergency_alert.txt", "w") as file:
                file.write("Emergency Alert: User is in a danger zone!\n")
        except Exception as e:
            st.error(f"Error sending SMS: {e}")

    def make_emergency_call():
        try:
            call = client.calls.create(
                twiml='<Response><Say>Your emergency contact has initiated an emergency call. Please check on them.</Say></Response>',
                to=to_number,
                from_=twilio_number
            )
            st.success(f"Call initiated: {call.sid}")
            
            # Write to the emergency alert file
            with open("emergency_alert.txt", "w") as file:
                file.write("Emergency Alert: Emergency call initiated!\n")
                
            return {"status": "success", "call_sid": call.sid}
        except Exception as e:
            st.error(f"Error initiating call: {e}")

    def show_risk_map():
        # Define locations with names for risk prediction
        locations_with_names = [
            (13.0827, 80.2707, 'Chennai'),  # Chennai city center
            (13.067439, 80.237617, 'Nungambakkam'),  # Nungambakkam
            (12.9719, 80.2108, 'Velachery'),  # Velachery
            (13.0007, 80.2565, 'T Nagar'),  # T Nagar
            (12.996, 80.2511, 'Mylapore'),  # Mylapore
            (13.0988, 80.2835, 'Anna Nagar'),  # Anna Nagar
            (13.0358, 80.2445, 'Adyar'),  # Adyar
            (13.0833, 80.2707, 'Royapettah'),  # Royapettah
            (13.1393, 80.2276, 'Madhavaram'),  # Madhavaram
            (13.0475, 80.2094, 'Guindy')  # Guindy
        ]

        # Get predicted risk levels for each location
        predicted_risks = predict_risk_levels(locations_with_names)

        # Generate and display the heatmap
        map_obj = plot_risk_map(predicted_risks)
        st_folium(map_obj, width=700, height=500)

    # Always display the main title at the top
    st.title("Femguard")
    
    # Communication Page Content
    st.header("Communication Page")
    st.write("Use the buttons below to check your location status or share your location or initiate an emergency call.")

    # Buttons
    if st.button("Safety Status"):
        st.session_state.page = 'safety_status'  # Redirect to safety status page

    if st.button("Send Location SMS"):
        send_location_sms()

    if st.button("Make Emergency Call"):
        make_emergency_call()

    if st.button("Risk Map"):
        show_risk_map()

    # Button to go back to the Home Page
    if st.button('Go to Home Page'):
        st.session_state.page = 'home'

# Function for safety status prediction
def safety_status_page():
    # Load model and encoders
    model = joblib.load('models/xgb_classifier_model.pkl')
    encoders = joblib.load('models/label_encoders.pkl')

    def predict_safety_status(input_data):
        # Apply encoders to input data
        input_data['Location'] = encode_with_fallback(input_data['Location'], encoders['Location'])
        input_data['Time_of_Day'] = encode_with_fallback(input_data['Time_of_Day'], encoders['Time_of_Day'])
        input_data['Weather_Conditions'] = encode_with_fallback(input_data['Weather_Conditions'], encoders['Weather_Conditions'])
        input_data['Population_Density'] = encode_with_fallback(input_data['Population_Density'], encoders['Population_Density'])
        input_data['Age_Group'] = encode_with_fallback(input_data['Age_Group'], encoders['Age_Group'])

        input_df = pd.DataFrame([input_data])

        probabilities = model.predict_proba(input_df)[0]

        if input_data['Location'] == encoders['Location'].transform(['Potheri'])[0]:
            probabilities[0] *= 0.5  # Reduce probability of 'Safe'
            probabilities[1] *= 1.5  # Increase probability of 'Unsafe'

        probabilities /= probabilities.sum()

        return 'Safe' if np.argmax(probabilities) == 0 else 'Unsafe'

    def generate_random_data(location):
        latitude = round(random.uniform(12.8, 13.2), 6)
        longitude = round(random.uniform(80.0, 80.3), 6)
        time_of_day = random.choice(['Morning', 'Afternoon', 'Evening', 'Night'])
        weather_conditions = random.choice(['Clear', 'Rainy', 'Foggy', 'Snowy'])
        population_density = random.choice(['Low', 'Medium', 'High'])
        nearby_facilities = random.randint(0, 10)
        age_group = random.choice(['Child', 'Teen', 'Adult', 'Senior'])

        input_data = {
            'Location': location,
            'Latitude': latitude,
            'Longitude': longitude,
            'Time_of_Day': time_of_day,
            'Weather_Conditions': weather_conditions,
            'Population_Density': population_density,
            'Nearby_Facilities': nearby_facilities,
            'Age_Group': age_group
        }

        return input_data

    st.title('Safety Status')
    st.write("Here, you can view the current safety status based on the latest data and alerts.")

    # User selects location only
    location = st.selectbox('Select Location:', options=encoders['Location'].classes_)

    if st.button('Predict Safety Status'):
        # Generate other inputs randomly
        input_data = generate_random_data(location)
        status = predict_safety_status(input_data)
        st.success(f'Predicted Safety Status: {status}')
        st.json(input_data)

    if st.button('Back to Home'):
        st.session_state.page = 'home'

# Main app
if 'page' not in st.session_state:
    st.session_state.page = 'home'

if st.session_state.page == 'home':
    communication_page()
elif st.session_state.page == 'safety_status':
    safety_status_page()
