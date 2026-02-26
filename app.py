"""
Career Jankari Chatbot - Backend
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from pathlib import Path
import pandas as pd

app = Flask(__name__)
CORS(app)

# ------------------------------
# KNOWLEDGE BASE
# ------------------------------

KNOWLEDGE_BASE = {
    "iits": {
        "keywords": ["iit", "indian institute of technology", "jee advanced"],
        "info": """
IITs (Indian Institutes of Technology) are premier engineering institutions in India.

Key Facts:
• Total IITs: 23 across India
• Admission: Through JEE Advanced exam
• Average Package: ₹15-20 LPA
"""
    },

    "nits": {
        "keywords": ["nit", "national institute of technology", "jee main"],
        "info": """
NITs (National Institutes of Technology) are top government engineering colleges.

Key Facts:
• Total NITs: 31
• Admission: Through JEE Main
• Average Package: ₹8-12 LPA
"""
    },

    "josaa": {
        "keywords": ["josaa", "counseling", "seat allocation"],
        "info": """
JoSAA (Joint Seat Allocation Authority) conducts IIT/NIT/IIIT counseling.

Process:
1. Registration
2. Choice Filling
3. Seat Allocation
4. Document Verification
"""
    }
}

# ------------------------------
# CHATBOT CLASS
# ------------------------------

class ChatBot:
    def __init__(self):
        # No CSV loading (safe for Render free tier)
        self.josaa_df = None

    def find_topic(self, query):
        query = query.lower()
        for topic, data in KNOWLEDGE_BASE.items():
            for keyword in data["keywords"]:
                if keyword in query:
                    return topic
        return None

    def get_response(self, query):
        if not query:
            return {"response": "Please enter a message."}

        topic = self.find_topic(query)

        if topic:
            return {
                "response": KNOWLEDGE_BASE[topic]["info"]
            }

        return {
            "response": "I can help with IIT, NIT, and JoSAA questions. Try asking about them."
        }

# ------------------------------
# INITIALIZE BOT
# ------------------------------

chatbot = ChatBot()

# ------------------------------
# ROUTES
# ------------------------------

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
        "bot_name": "Career Jankari Assistant",
        "version": "1.0"
    })
