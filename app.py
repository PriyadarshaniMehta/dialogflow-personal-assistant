import os
import requests
import random
from flask import Flask, request, jsonify, render_template, send_from_directory
from datetime import datetime
import pytz
from flask_cors import CORS

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

TASKS = []
NEWSDATA_API_KEY = os.getenv("NEWSDATA_API_KEY")

# Jokes database
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

# Greeting patterns
GREETINGS_IN = [
    "hello", "hi", "hey", "good morning", "good afternoon", "good evening",
    "howdy", "greetings", "what's up", "yo", "hi there", "hello there"
]

GREETINGS_OUT = [
    "Hello! How can I assist you today?",
    "Hi there! What can I help you with?",
    "Hey! Nice to see you. How can I help?",
    "Greetings! I'm here to help with weather, time, tasks, news, and jokes!",
    "Hello! Ready to tackle some tasks or just chat?",
    "Hi! I'm your friendly AI assistant. What's on your mind?"
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/debug-static')
def debug_static():
    import os
    result = []
    result.append("Current directory: " + os.getcwd())
    result.append("Files in current directory: " + str(os.listdir('.')))
    
    if os.path.exists('static'):
        result.append("Static directory exists")
        result.append("Files in static: " + str(os.listdir('static')))
        if os.path.exists('static/css'):
            result.append("CSS directory exists")
            result.append("CSS files: " + str(os.listdir('static/css')))
        if os.path.exists('static/js'):
            result.append("JS directory exists")
            result.append("JS files: " + str(os.listdir('static/js')))
    else:
        result.append("Static directory does NOT exist")
        
    if os.path.exists('templates'):
        result.append("Templates directory exists")
        result.append("Template files: " + str(os.listdir('templates')))
    else:
        result.append("Templates directory does NOT exist")
        
    return "<br>".join(result)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True, force=True)

    user_message = (
        data.get("query", "").lower()
        or data.get("queryResult", {}).get("queryText", "").lower()
    )

    # Greetings
    if any(greeting in user_message for greeting in GREETINGS_IN):
        return jsonify({"fulfillmentText": random.choice(GREETINGS_OUT)})

    # Jokes
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

    # Time
    if "time" in user_message or "clock" in user_message:
        try:
            ist = pytz.timezone("Asia/Kolkata")
            current_time = datetime.now(ist).strftime("%I:%M %p")
            return jsonify({"fulfillmentText": f"The current time in IST is {current_time}."})

        except Exception as e:
            return jsonify({"fulfillmentText": f"Time error: {str(e)}"})

    # Task Creation
    if "add task" in user_message or "create task" in user_message or "remind me" in user_message:
        task_text = (
            user_message.replace("add task", "")
            .replace("create task", "")
            .replace("remind me", "")
            .strip()
        )
        TASKS.append({"task": task_text})
        return jsonify({"fulfillmentText": f"Task added: {task_text}"})

    # Task List
    if "list tasks" in user_message or "show tasks" in user_message:
        if not TASKS:
            return jsonify({"fulfillmentText": "You have no tasks."})

        reply = "Here are your tasks:\n"
        for i, t in enumerate(TASKS, 1):
            reply += f"{i}. {t['task']}\n"

        return jsonify({"fulfillmentText": reply})

    # Task Delete
    if "delete task" in user_message:
        try:
            num = int(user_message.split()[-1])
            removed = TASKS.pop(num - 1)
            return jsonify({"fulfillmentText": f"Task deleted: {removed['task']}"} )
        except:
            return jsonify({"fulfillmentText": "Invalid task number to delete."})

    # News
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

    # Farewell
    if any(word in user_message for word in ["bye", "goodbye", "see you", "farewell", "quit", "exit"]):
        farewells = [
            "Goodbye! Have a great day!",
            "See you later! Don't hesitate to come back if you need anything!",
            "Farewell! Remember I'm here whenever you need assistance!",
            "Bye! Take care and stay productive!",
            "Goodbye! Hope to chat with you again soon!"
        ]
        return jsonify({"fulfillmentText": random.choice(farewells)})

    # Thank you responses
    if any(word in user_message for word in ["thank", "thanks", "appreciate"]):
        thanks_responses = [
            "You're welcome! Happy to help!",
            "Anytime! That's what I'm here for!",
            "No problem! Let me know if you need anything else!",
            "Glad I could assist! Don't hesitate to ask for more help!",
            "My pleasure! Feel free to ask me anything else!"
        ]
        return jsonify({"fulfillmentText": random.choice(thanks_responses)})

    # Fallback
    fallback_responses = [
        "I'm here to help with weather, time, tasks, news, and jokes! What would you like to know?",
        "I can tell you the weather, current time, help manage tasks, share news, or tell a joke. What would you like?",
        "Sorry, I didn't understand that. I can help with: weather, time, tasks, news, or tell you a joke!",
        "I'm not sure I follow. Try asking about weather, time, tasks, news, or ask for a joke!",
        "Let me help you! I can check weather, tell time, manage tasks, share news, or brighten your day with a joke!"
    ]
    return jsonify({"fulfillmentText": random.choice(fallback_responses)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
