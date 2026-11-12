import os
import datetime
from flask import Flask, request, jsonify
from pymongo import MongoClient

app = Flask(__name__)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
    client.server_info()
    db = client['nexcart_retail']
    db_status = "Connected to MongoDB"
except Exception:
    db = None
    db_status = "MongoDB not detected locally. Using in-memory fallback."

fallback_reviews = []

@app.route("/review", methods=["POST"])
def add_review():
    data = request.json
    review_doc = {
        "product_id": data.get("product_id"),
        "user_id": data.get("user_id", "anonymous"),
        "rating": data.get("rating"),
        "comment": data.get("comment"),
        "date": datetime.datetime.now(datetime.timezone.utc)
    }

    if db is not None:
        db.reviews.insert_one(review_doc)
        review_doc["_id"] = str(review_doc["_id"]) # Serialize for JSON
    else:
        fallback_reviews.append(review_doc)

    return jsonify({"message": "Review saved to MongoDB", "status": db_status})

@app.route("/reviews/<int:product_id>", methods=["GET"])
def get_reviews(product_id):
    if db is not None:
        cursor = db.reviews.find({"product_id": product_id}, {"_id": 0})
        reviews = list(cursor)
    else:
        reviews = [r for r in fallback_reviews if r.get("product_id") == product_id]
        
    return jsonify({"product_id": product_id, "reviews": reviews, "source": db_status})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8005, debug=True)