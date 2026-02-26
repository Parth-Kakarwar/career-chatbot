"""
Career Jankari Chatbot - AI + Knowledge Base Version
Stable OpenRouter Integration
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

# -----------------------------------
# CONFIG
# -----------------------------------

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

MODEL = "openai/gpt-oss-20b:free"

# -----------------------------------
# KNOWLEDGE BASE
# -----------------------------------

KNOWLEDGE_BASE = {
    "iits": {
        "keywords": ["iit", "indian institute of technology"],
        "info": "IITs are premier engineering institutes in India. Admission is through JEE Advanced."
    },
    "nits": {
        "keywords": ["nit", "national institute of technology"],
        "info": "NITs are top government engineering colleges. Admission is through JEE Main."
    },
    "josaa": {
        "keywords": ["josaa", "counseling"],
        "info": "JoSAA conducts centralized counseling for IIT, NIT, IIIT admissions."
    }
}

# -----------------------------------
# CHATBOT CLASS
# -----------------------------------

class ChatBot:

    def find_topic(self, query):
        query = query.lower()
        for topic, data in KNOWLEDGE_BASE.items():
            for keyword in data["keywords"]:
                if keyword in query:
                    return topic
        return None

    def call_openrouter(self, message):

        if not OPENROUTER_API_KEY:
            return "OpenRouter API key not configured."

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://career-chatbot-demo",
            "X-Title": "Career Jankari AI"
        }

        payload = {
            "model": MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": "You are Career Jankari AI assistant helping Indian students with career and college guidance."
                },
                {
                    "role": "user",
                    "content": message
                }
            ],
            "temperature": 0.7
        }

        try:
            response = requests.post(
                OPENROUTER_URL,
                headers=headers,
                json=payload,
                timeout=30
            )

            result = response.json()

            print("OpenRouter RAW response:", result)

            # Handle error response safely
            if "error" in result:
                return f"AI Error: {result['error']}"

            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]

            return "AI did not return a valid response."

        except Exception as e:
            return f"Error contacting AI service: {str(e)}"

    def get_response(self, query):

        if not query:
            return {"response": "Please enter a question."}

        topic = self.find_topic(query)

        if topic:
            return {"response": KNOWLEDGE_BASE[topic]["info"]}

        # Fallback to AI
        ai_response = self.call_openrouter(query)
        return {"response": ai_response}


chatbot = ChatBot()

# -----------------------------------
# ROUTES
# -----------------------------------

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    message = data.get("message", "")
    response = chatbot.get_response(message)
    return jsonify(response)

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "ai_enabled": True,
        "model": MODEL,
        "version": "3.0"
    })
