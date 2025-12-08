from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# ---------------------------------------------------------
# CONFIG — URL of Recommendation Agent
# ---------------------------------------------------------
RECOMMENDER_URL = "http://localhost:5000"   # change if needed


# ---------------------------------------------------------
# SALES AGENT CORE FUNCTIONS
# ---------------------------------------------------------
def get_user_recommendations(user_id: int):
    """Ask Recommendation Agent for personalized user recommendations."""
    try:
        url = f"{RECOMMENDER_URL}/recommendations/user/{user_id}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": f"Recommendation service failed: {str(e)}"}


def search_products(keyword: str):
    """Call /search/products from Recommendation Agent."""
    try:
        url = f"{RECOMMENDER_URL}/search/products"
        response = requests.get(url, params={"q": keyword})
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def keyword_recommendation(keyword: str):
    """Call keyword-based recommendation endpoint."""
    try:
        url = f"{RECOMMENDER_URL}/recommendations/keyword"
        response = requests.post(url, json={"keyword": keyword})
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}


# ---------------------------------------------------------
# SALES AGENT LOGIC
# ---------------------------------------------------------
@app.route("/sales/chat", methods=["POST"])
def chat_with_sales_agent():
    """
    Input:
    {
        "user_id": 1,
        "message": "suggest me some oats"
    }
    """
    data = request.json
    user_id = data.get("user_id")
    message = data.get("message", "").lower()

    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    # -------------------------
    # 1. If user message contains keywords
    # -------------------------
    words = message.split()

    # Basic NLP keyword detection
    search_term = None
    for w in words:
        if len(w) > 2:  # ignore "is", "to", "me", etc.
            search_term = w
            break

    response_payload = {}

    # -------------------------
    # 2. If user searches for a product (milk, bread, oats...)
    # -------------------------
    if search_term:
        keyword_result = keyword_recommendation(search_term)
        response_payload["keyword_search"] = keyword_result

    # -------------------------
    # 3. Always include personalized recommendations
    # -------------------------
    user_rec = get_user_recommendations(user_id)
    response_payload["personalized_recommendations"] = user_rec

    # -------------------------
    # 4. Sales agent response message
    # -------------------------
    bot_reply = "Here are some recommendations:\n"

    # Add keyword results if available
    if "matched_product" in keyword_result:
        bot_reply += f"\n🔍 Based on your search for '{search_term}', I found:\n"
        bot_reply += f"✔ {keyword_result['matched_product']['product_name']}\n"
        bot_reply += "\nSimilar products:\n"
        for item in keyword_result['similar_recommendations']:
            bot_reply += f"- {item['product_name']} (Score: {item['score']})\n"

    # Personalized recommendations
    if "recommendations" in user_rec:
        bot_reply += "\n🛒 Personalized for you:\n"
        for item in user_rec["recommendations"][:5]:
            bot_reply += f"- {item['product_name']} (Score: {item['score']})\n"

    response_payload["agent_reply"] = bot_reply

    return jsonify(response_payload)


# ---------------------------------------------------------
# HEALTH CHECK
# ---------------------------------------------------------
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "sales agent active"})


# ---------------------------------------------------------
# RUN SERVER
# ---------------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6000, debug=True)