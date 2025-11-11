import os
import requests
from flask import Flask, request, jsonify, render_template
from datetime import datetime
import pytz
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  

TASKS = []
NEWSDATA_API_KEY = os.getenv("NEWSDATA_API_KEY")

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True, force=True)

    user_message = (
        data.get("query", "").lower()
        or data.get("queryResult", {}).get("queryText", "").lower()
    )

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

    # Fallback
    return jsonify({"fulfillmentText": "I'm here to help!"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

