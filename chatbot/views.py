from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import random
import numpy as np
import nltk
import pickle
from tensorflow.keras.models import load_model
from nltk.stem import WordNetLemmatizer
from users.models import bear  # Import user model

# Initialize NLP Tools
nltk.download("punkt")
lemmatizer = WordNetLemmatizer()

# Load Chatbot Data
model = load_model("chatbot/chatbot_model.h5")
words = pickle.load(open("chatbot/words.pkl", "rb"))
classes = pickle.load(open("chatbot/classes.pkl", "rb"))

# Load Intents File
with open("chatbot/intents.json") as file:
    intents = json.load(file)

@csrf_exempt
def chatbot_api(request, user_id):
    """Handles chatbot messages and returns responses."""
    user = bear.objects.filter(uuid=user_id).first()

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get("message", "").strip()

            if not user_message:
                return JsonResponse({"error": "No message provided."}, status=400)

            # Process chatbot response using better Flask-based functions
            response = chatbot_response(user_message, user)
            return JsonResponse({"response": response})

        except Exception as e:
            return JsonResponse({"error": f"Server error: {e}"}, status=500)

    return render(request, "chatbot.html", {"user": user})

# ------------------- 🚀 IMPROVED CHATBOT FUNCTIONS 🚀 -------------------

def clean_up_sentence(sentence):
    """Tokenizes and lemmatizes input sentence."""
    sentence_words = nltk.word_tokenize(sentence)
    return [lemmatizer.lemmatize(word.lower()) for word in sentence_words]

def bag_of_words(sentence):
    """Converts sentence into a bag-of-words vector."""
    sentence_words = clean_up_sentence(sentence)
    return np.array([1 if w in sentence_words else 0 for w in words])

def predict_class(sentence):
    bow = bag_of_words(sentence)
    res = model.predict(np.array([bow]))[0]
    threshold = 0.7
    results = [{"intent": classes[i], "probability": res[i]} for i, r in enumerate(res) if r > threshold]
    results.sort(key=lambda x: x["probability"], reverse=True)
    
    # Debugging: Print the detected intent and its probability
    print(f"User input: {sentence}")
    print(f"Predicted intents: {results}")  

    return results


def get_response(predictions, user):
    if not predictions:
        return "I'm not sure I understand. Could you rephrase?"

    tag = predictions[0]["intent"]
    for intent in intents["intents"]:
        if intent["tag"] == tag:
            return random.choice(intent["responses"])

    return "I didn't quite get that. Can you clarify?"



def chatbot_response(user_input, user):
    """Processes input and returns chatbot response using enhanced logic."""
    predictions = predict_class(user_input)
    return get_response(predictions, user)
