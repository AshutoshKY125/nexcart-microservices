import os
import datetime
from flask import Flask, request, jsonify
from pymongo import MongoClient

app = Flask(__name__)

# Fulfill MongoDB Requirement
# Fallback to in-memory lists if MongoDB is not running locally yet
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
try:
    # Timeout set to 2 seconds so it doesn't hang if Mongo isn't installed
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
    client.server_info() 
    db = client['nexcart_retail']
    db_status = "Connected to MongoDB"
except Exception:
    db = None
    db_status = "MongoDB not detected locally. Using in-memory fallback."

# In-memory fallbacks for local testing without DB
fallback_grievances = []
fallback_feedback = []

def analyze_intent(text):
    """
    Core NLP routing logic. In a production environment, this can be 
    upgraded to an LLM or a trained neural network.
    """
    text = text.lower()
    if any(word in text for word in ["complain", "broken", "issue", "wrong", "grievance", "bad", "terrible"]):
        return "grievance"
    elif any(word in text for word in ["where", "navigate", "find", "search", "menu", "category"]):
        return "navigation"
    elif any(word in text for word in ["feedback", "suggest", "improve", "idea"]):
        return "feedback"
    else:
        return "support"

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_msg = data.get("message", "")
    user_id = data.get("user_id", "guest_user")
    
    intent = analyze_intent(user_msg)
    reply = ""
    timestamp = datetime.datetime.now(datetime.timezone.utc)

    if intent == "grievance":
        ticket = {"user_id": user_id, "message": user_msg, "status": "open", "date": timestamp}
        if db is not None:
            db.grievances.insert_one(ticket)
        else:
            fallback_grievances.append(ticket)
        reply = "I'm sorry you are facing an issue. I have logged a grievance ticket for our human support team."
        
    elif intent == "navigation":
        reply = "Looking for something? You can use the search bar at the top, or browse categories like Footwear, Electronics, and Home Office."
        
    elif intent == "feedback":
        feedback_entry = {"user_id": user_id, "message": user_msg, "date": timestamp}
        if db is not None:
            db.feedback.insert_one(feedback_entry)
        else:
            fallback_feedback.append(feedback_entry)
        reply = "Thank you for your feedback! We are always looking to improve our platform based on your suggestions."
        
    else:
        reply = "I am your NexCart AI assistant. I can help you navigate the store, log grievances, or take feedback. How can I help?"

    return jsonify({
        "intent": intent,
        "reply": reply,
        "db_status": db_status
    })

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "service": "chatbot", "database": db_status})

if __name__ == "__main__":
    # Runs on Port 8001 as defined in the master architecture
    app.run(host="0.0.0.0", port=8001, debug=True)