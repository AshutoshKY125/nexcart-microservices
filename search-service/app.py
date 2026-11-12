import os
from flask import Flask, request, jsonify
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

# Seed Catalog (In a real app, this replicates from the SQL DB or an Elasticsearch instance)
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

# 1. Prepare the text corpus (combining name, category, and tags for rich context)
corpus = [f"{p['name']} {p['category']} {p['tags']}" for p in CATALOG]

# 2. Fit the TF-IDF Vectorizer
vectorizer = TfidfVectorizer(stop_words='english')
tfidf_matrix = vectorizer.fit_transform(corpus)

@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("q", "").strip()
    
    if not query:
        return jsonify({"source": "search-microservice-empty", "results": CATALOG})
    
    # 3. Vectorize the incoming search query
    query_vec = vectorizer.transform([query])
    
    # 4. Calculate Cosine Similarity between query and the catalog corpus
    similarities = cosine_similarity(query_vec, tfidf_matrix).flatten()
    
    # 5. Filter and sort by highest similarity (threshold > 0.05 ensures relevance)
    related_indices = [i for i in similarities.argsort()[::-1] if similarities[i] > 0.05]
    
    # 6. Basic string matching fallback (for partial words before the vectorizer can catch them)
    if not related_indices:
        filtered = [p for p in CATALOG if query.lower() in p["name"].lower() or query.lower() in p["tags"].lower()]
        return jsonify({"source": "search-microservice-fallback", "results": filtered})

    results = [CATALOG[i] for i in related_indices]
    
    return jsonify({
        "source": "search-microservice-tfidf",
        "results": results,
        "top_score": float(max(similarities)) if related_indices else 0.0
    })

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "service": "search", "algorithm": "TF-IDF + Cosine Similarity"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8002, debug=True)