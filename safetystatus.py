import streamlit as st
import pandas as pd
import numpy as np
import joblib
import random

def safety_status_page():
    # Load model and encoders
    model = joblib.load('models/xgb_classifier_model.pkl')
    encoders = joblib.load('models/label_encoders.pkl')

    def predict_safety_status(input_data):
        # Apply encoders to input data
        for column, encoder in encoders.items():
            if column in input_data:
                input_data[column] = encoder.transform([input_data[column]])[0]
        input_df = pd.DataFrame([input_data])

        # Modify probabilities for Potheri
        probabilities = model.predict_proba(input_df)[0]
        if input_data['Location'] == encoders['Location'].transform(['Potheri'])[0]:
            probabilities[0] *= 0.5  # Reducing the probability of 'Safe'
            probabilities[1] *= 1.5  # Increasing the probability of 'Unsafe'
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
        st.json(input_data)  # Optionally display the randomized input data for transparency

    if st.button('Back to Home'):
        st.session_state.page = 'home'