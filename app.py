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

MODEL = "arcee-ai/trinity-large-preview:free"

# -----------------------------------
# KNOWLEDGE BASE
# -----------------------------------

KNOWLEDGE_BASE = {

    "iits": {
        "keywords": ["iit", "indian institute of technology", "jee advanced"],
        "info": """
📘 Indian Institutes of Technology (IITs)

IITs are India's premier public technical universities known for excellence in engineering, research, and innovation.

🔹 Total IITs: 23
🔹 Admission: JEE Advanced (after qualifying JEE Main)
🔹 Duration: 4-year B.Tech programs
🔹 Academic Strength: Strong research, global collaborations

🏆 Top IITs (Based on NIRF & reputation):
• IIT Madras
• IIT Delhi
• IIT Bombay
• IIT Kanpur
• IIT Kharagpur

💼 Placements (Approx 2024 Trends):
• Average Package: ₹15–25 LPA
• Top Packages: ₹1+ Crore (international offers)
• Top Recruiters: Google, Microsoft, Amazon, Goldman Sachs

🎯 Popular Branches:
• Computer Science Engineering (CSE)
• Electrical Engineering
• Mechanical Engineering
• Aerospace Engineering

Note: Admission is extremely competitive.
"""
    },

    "nits": {
        "keywords": ["nit", "national institute of technology", "jee main"],
        "info": """
📘 National Institutes of Technology (NITs)

NITs are top government engineering colleges funded by the Government of India.

🔹 Total NITs: 31
🔹 Admission: JEE Main
🔹 Home State + Other State Quota
🔹 Centrally funded institutions

🏆 Top NITs:
• NIT Trichy
• NIT Surathkal
• NIT Warangal
• NIT Calicut
• NIT Rourkela

💼 Placements (2024 Approx):
• Average Package: ₹8–15 LPA
• Highest Package: ₹40–60 LPA
• Strong in CSE, ECE, EE

🎯 Why Choose NIT?
• Strong alumni network
• Good infrastructure
• Lower competition than IITs
"""
    },

    "iiits": {
        "keywords": ["iiit", "indian institute of information technology"],
        "info": """
📘 Indian Institutes of Information Technology (IIITs)

IIITs specialize mainly in IT and Computer Science related fields.

🔹 Focus Areas: CSE, IT, AI, Data Science
🔹 Admission: JEE Main (most IIITs)
🔹 Some are PPP model institutions

🏆 Top IIITs:
• IIIT Hyderabad
• IIIT Bangalore
• IIIT Delhi
• IIIT Allahabad

💼 Placements:
• Average Package: ₹10–20 LPA
• Very strong in tech companies
• High coding culture

Best for students interested in software & AI fields.
"""
    },

    "josaa": {
        "keywords": ["josaa", "counseling", "seat allocation", "choice filling"],
        "info": """
📘 JoSAA Counseling (Joint Seat Allocation Authority)

JoSAA conducts centralized counseling for:
• IITs
• NITs
• IIITs
• GFTIs

📝 Process:
1. Registration
2. Choice Filling
3. Mock Allocation
4. Round 1–6 Seat Allocation
5. Seat Acceptance (Freeze/Float/Slide)
6. Document Verification

📌 Important Tips:
• Fill 80–100 choices
• Order strictly by preference
• Include safe + moderate + dream options
• Seat upgradation possible till final round

Official Website: https://josaa.nic.in
"""
    },

    "placements": {
        "keywords": ["placement", "package", "salary", "job", "companies"],
        "info": """
📘 Engineering Placements Overview (2024 Trends)

🏫 IITs:
• Avg: ₹15–25 LPA
• Top: ₹1–2 Cr
• International offers available

🏫 NITs:
• Avg: ₹8–15 LPA
• Top: ₹40–60 LPA

🏫 IIITs:
• Avg: ₹10–20 LPA
• Strong in tech companies

🏢 Top Recruiters:
• Google
• Microsoft
• Amazon
• Goldman Sachs
• Adobe
• Samsung
• Qualcomm

Placement depends on:
• Branch
• College reputation
• Student skill level
"""
    },

    "branches": {
        "keywords": ["branch", "stream", "cse", "ece", "mechanical", "civil", "electrical"],
        "info": """
📘 Popular Engineering Branches

💻 Computer Science (CSE)
• Highest demand
• Avg Package: ₹12–25 LPA
• Careers: Software Engineer, AI/ML Engineer, Data Scientist

📡 Electronics & Communication (ECE)
• Mix of hardware & software
• Avg: ₹8–15 LPA

⚡ Electrical Engineering (EE)
• Core + software options
• Avg: ₹8–12 LPA

⚙ Mechanical Engineering
• Core engineering field
• Avg: ₹6–10 LPA

🏗 Civil Engineering
• Construction & infrastructure
• Avg: ₹5–8 LPA

Emerging Fields:
• Artificial Intelligence
• Data Science
• Cyber Security
• Robotics
"""
    },

    "fees": {
        "keywords": ["fees", "cost", "scholarship", "loan"],
        "info": """
📘 Engineering Fees (Approx Annual)

🏫 IITs:
• ₹2–3 Lakhs per year
• Total 4 years: ₹10–12 Lakhs

🏫 NITs:
• ₹1.5–2.5 Lakhs per year

🏫 Private Colleges:
• ₹1–5 Lakhs per year depending on tier

🎓 Scholarships:
• Merit-based
• Category-based
• Income-based government schemes

🏦 Education Loans:
• Available up to ₹20 Lakhs
• Interest: 8–12%
• Moratorium period available
"""
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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
