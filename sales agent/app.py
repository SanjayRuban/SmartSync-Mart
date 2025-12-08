from fastapi import FastAPI, Request
import requests
import csv
import re

app = FastAPI()

PRODUCTS_FILE = "matched_250_products.csv"
products = []
active_users = set()

# ----------------------------
# LOAD CSV USING PURE PYTHON
# ----------------------------
with open(PRODUCTS_FILE, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        products.append({
            "product_id": int(row["product_id"]),
            "product_name": row["product_name"]
        })

# ----------------------------
# LOGIN
# ----------------------------
@app.post("/login/{user_id}")
def login(user_id: int):
    active_users.add(user_id)
    return {"message": "Login successful", "user_id": user_id}

# ----------------------------
# CHAT ROUTER (STRICT MODE)
# ----------------------------
@app.post("/chat/{user_id}")
async def chat(user_id: int, request: Request):

    if user_id not in active_users:
        return {"error": "User not logged in"}

    data = await request.json()
    user_msg = data.get("message", "").lower()

    # ✅ BUY INTENT → API ONLY
    if any(x in user_msg for x in ["buy", "purchase", "order", "shop"]):
        return {
            "choose": {
                "1": "/recommend/by-keyword",
                "2": f"/recommend/by-history/{user_id}"
            }
        }

    # ✅ NORMAL CHAT → OLLAMA → TERMINAL ONLY
    ollama_response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3",
            "prompt": user_msg,
            "stream": False
        }
    ).json()

    reply = ollama_response.get("response", "")

    print("\n[OLLAMA CHAT RESPONSE]")
    print(reply)
    print("-" * 50)

    return {"status": "chat_displayed_in_terminal_only"}

# ----------------------------
# OPTION 1 → HISTORY (MOCK)
# ----------------------------
@app.get("/recommend/by-history/{user_id}")
def recommend_by_history(user_id: int):
    top_products = products[:5]
    product_ids = [p["product_id"] for p in top_products]

    return {
        "api_endpoint": f"/recommend/by-history/{user_id}",
        "product_ids": product_ids
    }

# ----------------------------
# OPTION 2 → KEYWORD MATCH → ENDPOINT ONLY
# ----------------------------
@app.post("/recommend/by-keyword")
async def recommend_by_keyword(request: Request):

    data = await request.json()
    user_text = data.get("text", "").lower()

    keywords = extract_keywords(user_text)

    for kw in keywords:
        for product in products:
            if kw in product["product_name"].lower():
                pid = product["product_id"]
                return {"api_endpoint": f"/product/{pid}"}

    return {"error": "No matching product found"}

# ----------------------------
# PRODUCT DETAILS
# ----------------------------
@app.get("/product/{product_id}")
def product_details(product_id: int):
    for product in products:
        if product["product_id"] == product_id:
            return product

    return {"error": "Invalid product ID"}

# ----------------------------
# KEYWORD EXTRACTION
# ----------------------------
def extract_keywords(text):
    text = re.sub(r"[^a-zA-Z ]", "", text)
    words = text.split()

    stopwords = {
        "i", "need", "to", "buy", "want", "purchase",
        "order", "a", "the", "of", "for", "some"
    }

    return [w for w in words if w not in stopwords]
