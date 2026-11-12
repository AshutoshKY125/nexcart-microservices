import os
from flask import Flask, jsonify
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

# Seed Catalog (Consistent across services for local dev without a central database)
CATALOG = [
    {"id": 101, "name": "ASICS Gel-Excite 10 Running Shoes", "category": "Footwear", "price": 5999, "rating": 4.7, "stock": 18, "tags": "running sports shoes marathon footwear"},
    {"id": 102, "name": "Pro Wireless Noise-Canceling Headphones", "category": "Electronics", "price": 4499, "rating": 4.5, "stock": 25, "tags": "audio bluetooth music headset"},
    {"id": 103, "name": "Mechanical RGB Developer Keyboard", "category": "Electronics", "price": 3299, "rating": 4.8, "stock": 12, "tags": "coding laptop accessories switches"},
    {"id": 104, "name": "Lightweight Trail Running Jacket", "category": "Apparel", "price": 2499, "rating": 4.4, "stock": 30, "tags": "jacket windcheater sports apparel"},
    {"id": 105, "name": "Smart Fitness & Marathon Watch", "category": "Electronics", "price": 6999, "rating": 4.6, "stock": 9, "tags": "watch tracker heartrate running"},
    {"id": 106, "name": "Ergonomic Mesh Office Chair", "category": "Home Office", "price": 8999, "rating": 4.5, "stock": 7, "tags": "chair desk posture wfh"},
    {"id": 107, "name": "ASIAN Men's Casual Sneakers", "category": "Footwear", "price": 1299, "rating": 4.2, "stock": 40, "tags": "shoes casual sneakers walking"},
    {"id": 108, "name": "Sparx Active Sports Flip-Flops", "category": "Footwear", "price": 499, "rating": 4.3, "stock": 50, "tags": "sandals casual home footwear"},
    {"id": 109, "name": "Musafir Cafe & October Junction (Combo)", "category": "Books", "price": 399, "rating": 4.9, "stock": 15, "tags": "hindi literature novel reading"},
    {"id": 110, "name": "Sharten Laagoo - Hindi Poetry Collection", "category": "Books", "price": 250, "rating": 4.8, "stock": 20, "tags": "poetry poem literature hindi books"},
    {"id": 111, "name": "Realme 10 Pro 5G Armor Case", "category": "Accessories", "price": 299, "rating": 4.1, "stock": 60, "tags": "mobile cover phone case protection"},
    {"id": 112, "name": "Jabra Elite USB-C Headset", "category": "Electronics", "price": 3499, "rating": 4.6, "stock": 22, "tags": "audio earphones meeting calls"},
    {"id": 113, "name": "White Charcoal Pencils (Set of 3)", "category": "Art Supplies", "price": 199, "rating": 4.5, "stock": 35, "tags": "sketching drawing canvas art"},
    {"id": 114, "name": "Black Canvas Sketchpad A4", "category": "Art Supplies", "price": 350, "rating": 4.7, "stock": 28, "tags": "paper notebook drawing art"},
    {"id": 115, "name": "Organic Green Tea Leaves (250g)", "category": "Groceries", "price": 450, "rating": 4.4, "stock": 100, "tags": "tea health beverage diet"},
    {"id": 116, "name": "Stainless Steel Thermal Flask", "category": "Home & Kitchen", "price": 899, "rating": 4.5, "stock": 45, "tags": "water bottle travel hydration"},
    {"id": 117, "name": "Non-Slip Yoga Mat with Alignment", "category": "Fitness", "price": 1099, "rating": 4.8, "stock": 25, "tags": "exercise workout gym stretch"},
    {"id": 118, "name": "Motorbike Helmet DOT Approved", "category": "Automotive", "price": 2499, "rating": 4.6, "stock": 10, "tags": "bike safety riding motorcycle"},
    {"id": 119, "name": "Motorcycle Chain Lube & Cleaner", "category": "Automotive", "price": 550, "rating": 4.5, "stock": 30, "tags": "maintenance bike oil care"},
    {"id": 120, "name": "Vitamin C Face Serum 30ml", "category": "Beauty", "price": 699, "rating": 4.3, "stock": 55, "tags": "skincare face glow cosmetics"},
    {"id": 121, "name": "SPF 50 Matte Sunscreen", "category": "Beauty", "price": 499, "rating": 4.4, "stock": 40, "tags": "skincare summer face care"},
    {"id": 122, "name": "Smart Home RGB LED Bulb", "category": "Smart Home", "price": 799, "rating": 4.2, "stock": 80, "tags": "lighting wifi alexa google"},
    {"id": 123, "name": "Premium Arabica Coffee Beans (500g)", "category": "Groceries", "price": 850, "rating": 4.7, "stock": 40, "tags": "coffee caffeine morning beverage"},
    {"id": 124, "name": "Wireless Gaming Mouse", "category": "Electronics", "price": 1599, "rating": 4.5, "stock": 30, "tags": "computer laptop accessories rgb"},
    {"id": 125, "name": "Ergonomic Aluminum Laptop Stand", "category": "Home Office", "price": 1299, "rating": 4.8, "stock": 25, "tags": "desk setup posture accessory"},
    {"id": 126, "name": "Resistance Bands Set (5 Levels)", "category": "Fitness", "price": 699, "rating": 4.6, "stock": 50, "tags": "workout gym exercise home"}
]

# 1. Build Item-to-Item Similarity Matrix based on categories and tags
corpus = [f"{p['category']} {p['tags']}" for p in CATALOG]
vectorizer = TfidfVectorizer(stop_words='english')
tfidf_matrix = vectorizer.fit_transform(corpus)

# Calculate cosine similarity between all products
cosine_sim_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)

def get_recommendations(product_id, top_n=3):
    try:
        # Find the index of the requested product
        idx = next(i for i, p in enumerate(CATALOG) if p["id"] == product_id)
    except StopIteration:
        return []
    
    # Get similarity scores for this product against all others
    sim_scores = list(enumerate(cosine_sim_matrix[idx]))
    
    # Sort by highest similarity, ignoring the product itself (which would be 100% similar)
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = [score for score in sim_scores if score[0] != idx][:top_n]
    
    # Map back to product objects
    return [CATALOG[i[0]] for i in sim_scores]

@app.route("/recommend/<int:product_id>", methods=["GET"])
def recommend(product_id):
    recs = get_recommendations(product_id)
    return jsonify({
        "source": "recommendation-microservice-ml",
        "product_id": product_id,
        "recommendations": recs
    })

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "service": "recommendation", "algorithm": "Content-Based Item-to-Item Filtering"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8003, debug=True)