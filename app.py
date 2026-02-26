"""
Career Jankari Chatbot - Backend
AI-powered chatbot for answering student queries about colleges, admissions, and careers
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import json
from pathlib import Path
import re

app = Flask(__name__)
CORS(app)  # Allow embedding from careerjankari.com

# Knowledge Base - Add more as needed
KNOWLEDGE_BASE = {
    "iits": {
        "keywords": ["iit", "indian institute of technology", "jee advanced"],
        "info": """
IITs (Indian Institutes of Technology) are premier engineering institutions in India.

Key Facts:
• Total IITs: 23 across India
• Admission: Through JEE Advanced exam
• Top IITs: IIT Madras, IIT Delhi, IIT Bombay, IIT Kanpur
• Average Package: ₹15-20 LPA
• Top Packages: ₹1+ Crore

Popular Branches:
1. Computer Science (highest cutoff)
2. Electrical Engineering
3. Mechanical Engineering
4. Aerospace Engineering

JEE Advanced Cutoff (2024):
• General: ~10,000 rank for newer IITs
• OBC: ~15,000 rank
• SC/ST: Higher relaxation
        """
    },
    
    "nits": {
        "keywords": ["nit", "national institute of technology", "jee main"],
        "info": """
NITs (National Institutes of Technology) are top government engineering colleges.

Key Facts:
• Total NITs: 31 across India
• Admission: Through JEE Main exam
• Top NITs: NIT Trichy, NIT Surathkal, NIT Warangal
• Average Package: ₹8-12 LPA
• Top Packages: ₹40-50 LPA

Popular Branches:
1. Computer Science & Engineering
2. Electronics & Communication
3. Electrical Engineering
4. Mechanical Engineering

JEE Main Cutoff (2024):
• General: 15,000-95,000 rank (varies by NIT)
• Home State: Lower cutoffs
• Other State: Higher cutoffs
        """
    },
    
    "iiits": {
        "keywords": ["iiit", "indian institute of information technology"],
        "info": """
IIITs specialize in Information Technology and Computer Science.

Top IIITs:
1. IIIT Hyderabad (autonomous, very prestigious)
2. IIIT Bangalore
3. IIIT Delhi
4. IIIT Allahabad

Key Facts:
• Focus: IT, CS, and allied fields
• Admission: JEE Main (most), separate exams (some)
• Average Package: ₹10-15 LPA
• Strong industry connections

IIIT Hyderabad:
• Rank: Often compared to top IITs
• Research-oriented institution
• Cutoffs similar to mid-tier IITs
        """
    },
    
    "placement": {
        "keywords": ["placement", "package", "salary", "job", "companies"],
        "info": """
College Placements in India (2024):

IITs:
• Average: ₹15-20 LPA
• Highest: ₹1-2 Crore (International offers)
• Top Recruiters: Google, Microsoft, Amazon, Goldman Sachs

NITs:
• Average: ₹8-12 LPA
• Highest: ₹40-60 LPA
• Top Recruiters: Microsoft, Amazon, Samsung, Qualcomm

IIITs:
• Average: ₹10-15 LPA
• Highest: ₹50+ LPA
• Top Recruiters: Google, Amazon, Adobe

Top Recruiting Companies:
1. Microsoft
2. Google
3. Amazon
4. Goldman Sachs
5. Adobe
6. Samsung
7. Qualcomm
8. Intel

Note: Actual packages vary by branch, student performance, and market conditions.
        """
    },
    
    "josaa": {
        "keywords": ["josaa", "counseling", "choice filling", "seat allocation"],
        "info": """
JoSAA (Joint Seat Allocation Authority) Counseling:

Process:
1. Registration (after JEE results)
2. Choice Filling (select colleges/branches)
3. Mock Seat Allocation (practice round)
4. Seat Allocation (multiple rounds)
5. Accept/Freeze seat
6. Document Verification
7. Fee Payment

Important Points:
• Fill 80-100 choices for safety
• Order by preference (best first)
• Include safe, moderate, and reach options
• Seat upgradation possible in later rounds
• Once frozen, cannot participate further

Rounds (typically 6):
• Round 1-5: Regular allocation
• Round 6: Special/final round

Documents Needed:
✓ JEE scorecard
✓ 10th & 12th marksheets
✓ Category certificate (if applicable)
✓ ID proof
✓ Photographs
        """
    },
    
    "cutoff": {
        "keywords": ["cutoff", "closing rank", "opening rank", "rank"],
        "info": """
Understanding College Cutoffs:

Opening Rank: Highest rank admitted (best student)
Closing Rank: Lowest rank admitted (last student)

Cutoff Trends:
• Decrease over rounds (seats fill up)
• Vary by category (OPEN, OBC, SC, ST, EWS)
• Change yearly based on difficulty

Example (IIT Bombay CSE 2024):
• Opening Rank: 1
• Closing Rank: 66
• Only top 66 ranks got admission!

Factors Affecting Cutoff:
1. Number of applicants
2. Exam difficulty
3. Available seats
4. Previous year trends
5. New college opening

Pro Tip: Use closing rank + 20% buffer for safety
If closing rank is 5000, aim for rank 4000 or better.
        """
    },
    
    "branches": {
        "keywords": ["branch", "stream", "cse", "ece", "mechanical", "civil", "computer science"],
        "info": """
Popular Engineering Branches:

1. Computer Science & Engineering (CSE)
   • Highest demand, best placements
   • Average: ₹12-25 LPA
   • Skills: Coding, algorithms, AI/ML
   • Jobs: Software Engineer, Data Scientist

2. Electronics & Communication (ECE)
   • Hardware + Software mix
   • Average: ₹8-15 LPA
   • Skills: Circuit design, signal processing
   • Jobs: Chip design, Telecom, Software

3. Electrical Engineering (EE)
   • Power systems, electronics
   • Average: ₹8-12 LPA
   • Skills: Circuit theory, power systems
   • Jobs: Core companies, Software

4. Mechanical Engineering
   • Traditional, versatile branch
   • Average: ₹6-10 LPA
   • Skills: Thermodynamics, mechanics
   • Jobs: Automobile, Manufacturing

5. Civil Engineering
   • Infrastructure, construction
   • Average: ₹5-8 LPA
   • Skills: Structures, surveying
   • Jobs: Construction, Government

Emerging Branches:
• Artificial Intelligence & ML
• Data Science
• Cyber Security
• Robotics
        """
    },
    
    "fees": {
        "keywords": ["fees", "cost", "scholarship", "loan", "expenses"],
        "info": """
Engineering College Fees (Annual):

IITs:
• Tuition: ₹2-2.5 Lakh/year
• Hostel: ₹15,000-30,000/year
• Total: ~₹2.5-3 Lakh/year
• Total (4 years): ₹10-12 Lakh

NITs:
• Tuition: ₹1.5-2 Lakh/year
• Hostel: ₹10,000-25,000/year
• Total: ~₹2-2.5 Lakh/year
• Total (4 years): ₹8-10 Lakh

Private Colleges:
• Tier 1 (BITS, VIT): ₹3-5 Lakh/year
• Tier 2: ₹1.5-3 Lakh/year
• Tier 3: ₹50,000-1.5 Lakh/year

Scholarships Available:
✓ Merit-based (institute scholarships)
✓ Government scholarships (based on income)
✓ Category-based (SC/ST/OBC)
✓ State scholarships

Education Loans:
• Available from all major banks
• Up to ₹20 Lakh easily
• Interest: 8-12% per annum
• Moratorium: During study + 1 year
        """
    }
}

class ChatBot:
    def __init__(self, josaa_data_path=None):
        """Initialize chatbot with JoSAA data if available"""
        self.josaa_df = None
        if josaa_data_path and Path(josaa_data_path).exists():
            try:
                self.josaa_df = pd.read_csv(josaa_data_path)
                print(f"✓ Loaded {len(self.josaa_df)} JoSAA records")
            except:
                print("! Could not load JoSAA data")
    
    def find_relevant_topic(self, query):
        """Find which topic the query is about"""
        query_lower = query.lower()
        
        # Check each topic's keywords
        for topic, data in KNOWLEDGE_BASE.items():
            for keyword in data["keywords"]:
                if keyword in query_lower:
                    return topic
        
        # Check for specific queries
        if any(word in query_lower for word in ["compare", "vs", "versus", "difference"]):
            if "iit" in query_lower and "nit" in query_lower:
                return "iit_vs_nit"
        
        return None
    
    def get_college_info(self, query):
        """Get specific college information from JoSAA data"""
        if self.josaa_df is None:
            return None
        
        query_lower = query.lower()
        
        # Extract college name
        colleges = self.josaa_df['Institute'].unique()
        for college in colleges:
            if college.lower() in query_lower:
                # Get all programs for this college
                college_data = self.josaa_df[self.josaa_df['Institute'] == college]
                
                # Get top 5 programs by closing rank
                top_programs = college_data.nsmallest(5, 'Closing Rank')
                
                response = f"**{college}**\n\n"
                response += f"Total Programs: {len(college_data)}\n\n"
                response += "Top 5 Competitive Programs:\n"
                
                for idx, row in top_programs.iterrows():
                    response += f"\n{row['Academic Program Name']}\n"
                    response += f"  • Closing Rank: {row['Closing Rank']}\n"
                    response += f"  • Seat Type: {row['Seat Type']}\n"
                
                return response
        
        return None
    
    def get_response(self, query):
        """Main function to get chatbot response"""
        
        # Check for greetings
        greetings = ["hi", "hello", "hey", "namaste"]
        if any(greet in query.lower() for greet in greetings):
            return {
                "response": """👋 Hello! I'm Career Jankari's AI assistant.

I can help you with:
• IIT/NIT/IIIT information
• JoSAA counseling process
• College cutoffs and rankings
• Placement statistics
• Branch selection advice
• Fees and scholarships

What would you like to know?""",
                "type": "greeting"
            }
        
        # Check for specific college info from database
        college_info = self.get_college_info(query)
        if college_info:
            return {
                "response": college_info,
                "type": "database",
                "source": "JoSAA Data 2024"
            }
        
        # Find relevant topic
        topic = self.find_relevant_topic(query)
        
        if topic == "iit_vs_nit":
            return {
                "response": """**IIT vs NIT Comparison:**

**IITs (Indian Institutes of Technology):**
✅ Higher prestige and brand value
✅ Better average placements (₹15-20L)
✅ Stronger alumni network globally
✅ More research opportunities
❌ Harder to get in (JEE Advanced)
❌ Slightly higher fees

**NITs (National Institutes of Technology):**
✅ Easier admission (JEE Main only)
✅ Good placements (₹8-12L average)
✅ Present in most states
✅ Lower fees than private colleges
❌ Less brand value than IITs
❌ Placement varies by NIT

**Bottom Line:**
• Top IITs > Top NITs > Lower IITs ≈ Top NITs
• NIT in good branch > IIT in poor branch
• Consider: Brand vs Branch trade-off

Would you like specific comparisons?""",
                "type": "comparison"
            }
        
        if topic and topic in KNOWLEDGE_BASE:
            return {
                "response": KNOWLEDGE_BASE[topic]["info"],
                "type": "knowledge_base",
                "topic": topic
            }
        
        # Default response for unknown queries
        return {
            "response": """I'm not sure about that specific question. 

I can help you with:
📚 College Information (IIT, NIT, IIIT)
📊 Placement Statistics
✍️ JoSAA Counseling Process
🎯 Branch Selection
💰 Fees & Scholarships
📈 Cutoff Trends

Try asking:
• "Tell me about IITs"
• "What are the placements at NITs?"
• "How does JoSAA counseling work?"
• "What is the cutoff for IIT Bombay?"

Or visit our detailed guides at careerjankari.com""",
            "type": "fallback"
        }

# Global chatbot instance
chatbot = ChatBot('josaa_data_2024_round5.csv')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Chat endpoint"""
    try:
        data = request.json
        query = data.get('message', '')
        
        if not query:
            return jsonify({'error': 'No message provided'}), 400
        
        response = chatbot.get_response(query)
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'bot_name': 'Career Jankari Assistant',
        'version': '1.0'
    })

if __name__ == '__main__':
    print("\n" + "="*60)
    print("Career Jankari Chatbot - Backend")
    print("="*60)
    print("\n🤖 Bot initialized")
    print("📍 API: http://localhost:5001")
    print("💬 Endpoint: POST /api/chat")
    print("\nReady to answer student queries!")
    print("="*60 + "\n")
    
    app.run(host="0.0.0.0", port=10000)
