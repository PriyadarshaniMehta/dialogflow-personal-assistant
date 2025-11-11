import os
import requests
import random
from flask import Flask, request, jsonify
from datetime import datetime
import pytz
from flask_cors import CORS

app = Flask(__name__)
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
    "Hello! I'm Persona, your personal assistant. How can I help you today?",
    "Hi there! Persona here, ready to assist. What's on your mind?",
    "Hey! Nice to see you. I'm Persona, your AI assistant. How can I help?",
    "Greetings! I'm Persona, here to help with various tasks and have a chat!",
    "Hello! I'm Persona, your friendly assistant. Ready to tackle some tasks or just chat?",
    "Hi! Persona at your service. What can I help you with today?"
]

# General conversation responses
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

# Complete HTML with new color scheme and Persona branding
HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Persona - Your AI Assistant</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }

        .chat-container {
            width: 100%;
            max-width: 800px;
            height: 80vh;
            background-color: #ffffff;
            border-radius: 20px;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
            display: flex;
            flex-direction: column;
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }

        .chat-header {
            background: linear-gradient(to right, #ff6b6b, #ff8e8e);
            color: white;
            padding: 25px;
            text-align: center;
            border-bottom: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }

        .chat-header h1 {
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 5px;
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.2);
        }

        .chat-header p {
            margin-top: 5px;
            opacity: 0.9;
            font-size: 16px;
        }

        .chatbox {
            flex: 1;
            padding: 25px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 20px;
            background-color: #f8f9fa;
        }

        .message {
            max-width: 80%;
            padding: 15px 20px;
            border-radius: 20px;
            line-height: 1.5;
            position: relative;
            word-wrap: break-word;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            animation: fadeIn 0.3s ease-in;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .user {
            align-self: flex-end;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border-bottom-right-radius: 5px;
        }

        .bot {
            align-self: flex-start;
            background: linear-gradient(135deg, #ff6b6b, #ff8e8e);
            color: white;
            border-bottom-left-radius: 5px;
        }

        .input-area {
            display: flex;
            padding: 20px;
            border-top: 1px solid #e0e0e0;
            background-color: #ffffff;
            box-shadow: 0 -4px 12px rgba(0, 0, 0, 0.05);
        }

        #userInput {
            flex: 1;
            padding: 15px 20px;
            border: 2px solid #e0e0e0;
            border-radius: 30px;
            outline: none;
            font-size: 16px;
            transition: all 0.3s;
            background-color: #f8f9fa;
        }

        #userInput:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2);
            background-color: #ffffff;
        }

        .send-button {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            border-radius: 50%;
            width: 55px;
            height: 55px;
            margin-left: 15px;
            cursor: pointer;
            display: flex;
            justify-content: center;
            align-items: center;
            transition: all 0.3s;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        }

        .send-button:hover {
            transform: scale(1.05) rotate(5deg);
            box-shadow: 0 6px 15px rgba(102, 126, 234, 0.4);
        }

        .send-button:active {
            transform: scale(0.98);
        }

        .send-button svg {
            width: 24px;
            height: 24px;
        }

        .typing-indicator {
            display: none;
            align-self: flex-start;
            background: linear-gradient(135deg, #ff6b6b, #ff8e8e);
            color: white;
            padding: 15px 20px;
            border-radius: 20px;
            border-bottom-left-radius: 5px;
            font-style: italic;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }

        .typing-dots {
            display: inline-block;
        }

        .typing-dots span {
            animation: typing 1.4s infinite;
            display: inline-block;
        }

        .typing-dots span:nth-child(2) {
            animation-delay: 0.2s;
        }

        .typing-dots span:nth-child(3) {
            animation-delay: 0.4s;
        }

        @keyframes typing {
            0%, 60%, 100% {
                transform: translateY(0);
            }
            30% {
                transform: translateY(-5px);
            }
        }

        /* Scrollbar styling */
        .chatbox::-webkit-scrollbar {
            width: 8px;
        }

        .chatbox::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 10px;
        }

        .chatbox::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, #667eea, #764ba2);
            border-radius: 10px;
        }

        .chatbox::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(135deg, #5a6fd8, #6a4190);
        }

        /* Responsive design */
        @media (max-width: 600px) {
            .chat-container {
                height: 90vh;
                border-radius: 15px;
            }
            
            .message {
                max-width: 90%;
            }
            
            .chat-header h1 {
                font-size: 24px;
            }
            
            .chat-header {
                padding: 20px;
            }
            
            .chatbox {
                padding: 20px;
            }
        }

        .welcome-message {
            text-align: center;
            padding: 10px;
            color: #666;
            font-size: 14px;
            font-style: italic;
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <h1>Persona</h1>
            <p>Your Personal AI Assistant</p>
        </div>
        <div class="chatbox" id="chatbox">
            <div class="message bot">
                <strong>👋 Hello! I'm Persona, your personal AI assistant!</strong>
                <br><br>I can help you with:
                <br>• 🌤️ Weather information
                <br>• ⏰ Current time
                <br>• ✅ Task management
                <br>• 📰 Latest news
                <br>• 😄 Jokes to brighten your day
                <br>• 💬 General conversation
                <br><br>Feel free to ask me anything or just say hello!
            </div>
        </div>
        <div class="typing-indicator" id="typingIndicator">
            Persona is thinking<span class="typing-dots"><span>.</span><span>.</span><span>.</span></span>
        </div>
        <div class="input-area">
            <input type="text" id="userInput" placeholder="Chat with Persona..." autocomplete="off">
            <button class="send-button" id="sendButton">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M3.478 2.404a.75.75 0 0 0-.926.941l2.432 7.905H13.5a.75.75 0 0 1 0 1.5H4.984l-2.432 7.905a.75.75 0 0 0 .926.94 60.519 60.519 0 0 0 18.445-8.986.75.75 0 0 0 0-1.218A60.517 60.517 0 0 0 3.478 2.404Z" />
                </svg>
            </button>
        </div>
    </div>

    <script>
        console.log("Persona chat interface loaded");
        
        // Wait for DOM to be fully loaded
        document.addEventListener('DOMContentLoaded', function() {
            console.log("DOM fully loaded");
            
            const input = document.getElementById("userInput");
            const chatbox = document.getElementById("chatbox");
            const typingIndicator = document.getElementById("typingIndicator");
            const sendButton = document.getElementById("sendButton");

            if (!input || !chatbox || !typingIndicator || !sendButton) {
                console.error("One or more required elements not found");
                return;
            }

            function sendMessage() {
                let text = input.value.trim();
                console.log("Sending message:", text);
                
                if (text === "") return;

                // Add user message to chat
                chatbox.innerHTML += `<div class="message user">${text}</div>`;
                chatbox.scrollTop = chatbox.scrollHeight;

                input.value = "";
                
                // Show typing indicator
                typingIndicator.style.display = 'block';
                chatbox.scrollTop = chatbox.scrollHeight;

                // Send request to Flask backend
                fetch("/webhook", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        query: text   
                    })
                })
                .then(response => {
                    console.log("Response status:", response.status);
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    console.log("Response data:", data);
                    // Hide typing indicator
                    typingIndicator.style.display = 'none';
                    
                    let reply = data.fulfillmentText || "I'm not sure how to respond to that. Can you try asking differently?";
                    chatbox.innerHTML += `<div class="message bot">${reply}</div>`;
                    chatbox.scrollTop = chatbox.scrollHeight;
                })
                .catch(err => {
                    console.error("Fetch error:", err);
                    // Hide typing indicator
                    typingIndicator.style.display = 'none';
                    
                    chatbox.innerHTML += `<div class="message bot">Sorry, there was an error connecting. Please try again.</div>`;
                    chatbox.scrollTop = chatbox.scrollHeight;
                });
            }

            // Add event listener for Enter key
            input.addEventListener("keydown", function(e) {
                if (e.key === "Enter") {
                    console.log("Enter key pressed");
                    sendMessage();
                }
            });

            // Add event listener for send button
            sendButton.addEventListener("click", function() {
                console.log("Send button clicked");
                sendMessage();
            });

            // Focus on input field when page loads
            input.focus();

            console.log("Persona is ready to chat!");
        });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return HTML

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

    # General conversation
    for pattern, responses in GENERAL_CONVERSATION.items():
        if pattern in user_message:
            return jsonify({"fulfillmentText": random.choice(responses)})

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

    # Fallback - more conversational
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
