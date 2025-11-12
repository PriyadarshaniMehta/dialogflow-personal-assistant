import os
import requests
import random
from flask import Flask, request, jsonify, send_file
from datetime import datetime
import pytz
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

TASKS = []
NEWSDATA_API_KEY = os.getenv("NEWSDATA_API_KEY")


JOKES = [
    "Why don't scientists trust atoms? Because they make up everything!",
    "Why did the scarecrow win an award? He was outstanding in his field!",
    "Why don't eggs tell jokes? They'd crack each other up!",
    "What do you call a fake noodle? An impasta!",
    "Why did the math book look so sad? Because it had too many problems!",
    "What do you call a bear with no teeth? A gummy bear!",
    "Why don't skeletons fight each other? They don't have the guts!",
    "What do you call a sleeping bull? A bulldozer!",
    "Why did the coffee file a police report? It got mugged!",
    "What do you call a fish wearing a crown? A king fish!",
    "Why don't programmers like nature? It has too many bugs!",
    "What do you call a programmer from Finland? Nerdic!",
    "Why do Java developers wear glasses? Because they can't C#!",
    "How many programmers does it take to change a light bulb? None, that's a hardware problem!",
    "Why do Python developers prefer snakes? Because they're afraid of commitment issues!"
]


GREETINGS_IN = [
    "hello", "hi", "hey", "good morning", "good afternoon", "good evening",
    "howdy", "greetings", "what's up", "yo", "hi there", "hello there"
]

GREETINGS_OUT = [
    "Hello! I'm Persona, your personal assistant. How can I help you today?",
    "Hi there! Persona here, ready to assist. What's on your mind?",
    "Hey! Nice to see you. I'm Persona, your AI assistant. How can I help?",
    "Greetings! I'm Persona, here to help with various tasks and have a chat!",
    "Hello! I'm Persona, your friendly assistant. Ready to tackle some tasks or just chat?",
    "Hi! Persona at your service. What can I help you with today?"
]

GENERAL_CONVERSATION = {
    "how are you": [
        "I'm doing great, thank you for asking! How about you?",
        "I'm functioning perfectly! Just here waiting to help you.",
        "I'm doing well! Ready to assist with whatever you need.",
        "I'm excellent! Hope you're having a good day too."
    ],
    "what is your name": [
        "I'm Persona, your personal AI assistant!",
        "My name is Persona! I'm here to help you.",
        "You can call me Persona. Nice to meet you!",
        "I'm Persona, your digital companion and assistant."
    ],
    "who created you": [
        "I was created by a developer to be your helpful AI assistant!",
        "I'm the creation of a developer who wanted to make a useful chatbot.",
        "I was developed to assist people like you with various tasks and conversations.",
        "A developer built me to be your personal assistant and conversation partner."
    ],
    "what can you do": [
        "I can help with weather, time, task management, news, jokes, and general conversation!",
        "I can check weather, tell time, manage tasks, share news, tell jokes, and chat with you!",
        "As Persona, I assist with weather info, time, tasks, news, humor, and friendly conversation.",
        "I'm here to help with practical tasks and keep you company with conversation!"
    ],
    "how old are you": [
        "I'm an AI, so I don't have an age in the traditional sense!",
        "As an AI, I exist in digital space without a physical age.",
        "I was recently created, so you could say I'm quite young!",
        "Age is just a number for humans - I'm timeless and always here to help."
    ],
    "where are you from": [
        "I exist in the digital world, available wherever you need me!",
        "I live in the cloud, ready to assist you from anywhere.",
        "I'm from the internet! My home is wherever there's a connection.",
        "I'm a digital native, born from code and living in servers."
    ],
    "tell me about yourself": [
        "I'm Persona, your AI assistant! I love helping people with tasks and having friendly conversations.",
        "I'm Persona - a helpful AI that enjoys assisting with weather, time, tasks, news, and chats!",
        "I'm Persona, your digital companion. I'm here to make your day easier and more enjoyable!",
        "I'm Persona! I specialize in practical assistance and friendly conversation to help you out."
    ]
}

@app.route('/')
def index():
    return send_file('ui.html')

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True, force=True)

    user_message = (
        data.get("query", "").lower()
        or data.get("queryResult", {}).get("queryText", "").lower()
    )

    
    if any(greeting in user_message for greeting in GREETINGS_IN):
        return jsonify({"fulfillmentText": random.choice(GREETINGS_OUT)})

   
    for pattern, responses in GENERAL_CONVERSATION.items():
        if pattern in user_message:
            return jsonify({"fulfillmentText": random.choice(responses)})

    
    if "joke" in user_message or "funny" in user_message or "make me laugh" in user_message:
        return jsonify({"fulfillmentText": random.choice(JOKES)})

    # Weather
    if "weather" in user_message or "temperature" in user_message:
        try:
            url = "https://api.open-meteo.com/v1/forecast?latitude=28.625&longitude=77.25&current_weather=true"
            weather_json = requests.get(url).json()

            current = weather_json.get("current_weather", {})
            temp = current.get("temperature")
            wind = current.get("windspeed")

            return jsonify({"fulfillmentText": f"The current temperature is {temp}°C with wind speed {wind} km/h."})

        except Exception as e:
            return jsonify({"fulfillmentText": f"Weather API error: {str(e)}"})

    
    if "time" in user_message or "clock" in user_message:
        try:
            ist = pytz.timezone("Asia/Kolkata")
            current_time = datetime.now(ist).strftime("%I:%M %p")
            return jsonify({"fulfillmentText": f"The current time in IST is {current_time}."})

        except Exception as e:
            return jsonify({"fulfillmentText": f"Time error: {str(e)}"})

    
    if "add task" in user_message or "create task" in user_message or "remind me" in user_message:
        task_text = (
            user_message.replace("add task", "")
            .replace("create task", "")
            .replace("remind me", "")
            .strip()
        )
        TASKS.append({"task": task_text})
        return jsonify({"fulfillmentText": f"Task added: {task_text}"})

    
    if "list tasks" in user_message or "show tasks" in user_message:
        if not TASKS:
            return jsonify({"fulfillmentText": "You have no tasks."})

        reply = "Here are your tasks:\n"
        for i, t in enumerate(TASKS, 1):
            reply += f"{i}. {t['task']}\n"

        return jsonify({"fulfillmentText": reply})

    
    if "delete task" in user_message:
        try:
            num = int(user_message.split()[-1])
            removed = TASKS.pop(num - 1)
            return jsonify({"fulfillmentText": f"Task deleted: {removed['task']}"} )
        except:
            return jsonify({"fulfillmentText": "Invalid task number to delete."})

    
    if "news" in user_message:
        try:
            url = f"https://newsdata.io/api/1/news?apikey={NEWSDATA_API_KEY}"
            news_json = requests.get(url).json()
            articles = news_json.get("results", [])

            top3 = [a.get("title") for a in articles[:3]]
            reply = "Latest headlines:\n" + "\n".join([f"- {h}" for h in top3])

            return jsonify({"fulfillmentText": reply})

        except Exception as e:
            return jsonify({"fulfillmentText": f"News error: {str(e)}"})

    
    if any(word in user_message for word in ["bye", "goodbye", "see you", "farewell", "quit", "exit"]):
        farewells = [
            "Goodbye! Have a great day!",
            "See you later! Don't hesitate to come back if you need anything!",
            "Farewell! Remember I'm here whenever you need assistance!",
            "Bye! Take care and stay productive!",
            "Goodbye! Hope to chat with you again soon!"
        ]
        return jsonify({"fulfillmentText": random.choice(farewells)})

    
    if any(word in user_message for word in ["thank", "thanks", "appreciate"]):
        thanks_responses = [
            "You're welcome! Happy to help!",
            "Anytime! That's what I'm here for!",
            "No problem! Let me know if you need anything else!",
            "Glad I could assist! Don't hesitate to ask for more help!",
            "My pleasure! Feel free to ask me anything else!"
        ]
        return jsonify({"fulfillmentText": random.choice(thanks_responses)})

    
    fallback_responses = [
        "I'm Persona, your personal assistant! I can help with weather, time, tasks, news, jokes, or just chat.",
        "That's interesting! As Persona, I specialize in practical help and friendly conversation.",
        "I'm not quite sure about that, but I'd love to help with something else!",
        "Hmm, I'm still learning! Maybe try asking about weather, time, tasks, news, or tell me about yourself?",
        "I'm Persona, here to make your day better! How can I assist you right now?"
    ]
    return jsonify({"fulfillmentText": random.choice(fallback_responses)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
