import streamlit as st
import random
import json
import torch
import numpy as np
import re
from utils.ChatBotUtils import NeuralNet, bag_of_words

device = torch.device('cpu')

# Define a function to tokenize input sentences
def tokenize(sentence):
    return re.findall(r'\w+', sentence.lower())

# Define a function to stem words to their root form
def stem(word):
    suffixes = ['ing', 'ly', 'ed', 'ious', 'ies', 'ive', 'es', 's', 'ment']
    for suffix in suffixes:
        if word.endswith(suffix):
            return word[:-len(suffix)]
    return word

class ChatBotApp:
    def __init__(self):
        self.load_model()

    def load_model(self):
        with open('intents.json', 'r') as json_data:
            self.intents = json.load(json_data)
        FILE = "data.pth"
        data = torch.load(FILE, map_location=device)
        self.model = NeuralNet(data["input_size"], data["hidden_size"], data["output_size"]).to(device)
        self.model.load_state_dict(data["model_state"])
        self.model.eval()
        self.all_words = data['all_words']
        self.tags = data['tags']

    def predict_class(self, message):
        sentence = tokenize(message)
        X = bag_of_words([stem(word) for word in sentence], self.all_words)
        X = torch.from_numpy(X.reshape(1, X.shape[0])).to(device)
        output = self.model(X)
        _, predicted = torch.max(output, dim=1)
        tag = self.tags[predicted.item()]
        prob = torch.softmax(output, dim=1)[0][predicted.item()]
        return {"tag": tag, "probability": prob.item()}

    def reply(self, message):
        output = self.predict_class(message)
        if output["probability"] > 0.75:
            for intent in self.intents['intents']:
                if intent['tag'] == output["tag"]:
                    return random.choice(intent['responses'])
        return "I'm sorry, I didn't understand that."

def chatbot_page():
    st.title("Chatbot")
    app = ChatBotApp()
    if 'history' not in st.session_state:
        st.session_state.history = []
    user_message = st.text_input("You:", "")
    response = ""
    if st.button("Send") and user_message:
        response = app.reply(user_message)
        st.session_state.history.append(f"You: {user_message}")
        st.session_state.history.append(f"Chatbot: {response}")

    if response:
        st.write("### Response")
        st.info(response)
        
    st.write("### Chat History")
    for message in st.session_state.history:
        st.text_area(label='', value=message, height=50, key=message)

    # Button to go back to the Home Page
    if st.button('Go Back to Home'):
        st.session_state.page = 'home'

# To run the chatbot_page function
if __name__ == "__main__":
    chatbot_page()