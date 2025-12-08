import ollama
import time
import uuid
import firebase_admin
from firebase_admin import credentials, firestore

# ==========================================================
# 🔥 FIREBASE INITIALIZATION
# ==========================================================

cred = credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# ==========================================================
# 🔹 KEYWORD BASED RECOMMENDATION (OPTION 2)
# ==========================================================

def get_recommendations_from_keyword(statement):
    print(f"\n🤖 Agent: Analyzing your statement: '{statement}'")

    keyword_prompt = f"""
    Extract only ONE main product keyword from the sentence below.
    Return ONLY the keyword, no explanation.

    Sentence: {statement}
    """

    keyword_response = ollama.chat(
        model="phi3",
        messages=[
            {"role": "system", "content": "You are an AI that extracts product keywords."},
            {"role": "user", "content": keyword_prompt}
        ]
    )

    extracted_keyword = keyword_response["message"]["content"].strip().lower()
    print(f"🔍 Extracted Keyword: '{extracted_keyword}'")

    request_id = str(uuid.uuid4())

    db.collection("requests").document(request_id).set({
        "type": "keyword",
        "keyword": extracted_keyword,
        "status": "pending",
        "timestamp": time.time()
    })

    wait_for_response(request_id)

# ==========================================================
# 🔹 USER ID BASED RECOMMENDATION (OPTION 1)
# ==========================================================

def get_recommendations_from_user(user_id):
    print(f"\n👤 Fetching recommendations for User ID: {user_id}")

    request_id = str(uuid.uuid4())

    db.collection("requests").document(request_id).set({
        "type": "user",
        "user_id": str(user_id),   # send as string
        "n": 10,
        "status": "pending",
        "timestamp": time.time()
    })

    wait_for_response(request_id)

# ==========================================================
# 🔹 COMMON RESPONSE HANDLER
# ==========================================================

def wait_for_response(request_id):
    print("☁️ Waiting for cloud response...")

    while True:
        time.sleep(1)
        doc = db.collection("responses").document(request_id).get()

        if doc.exists:
            recommendations = doc.to_dict()

            print("\n--- 🛍️ Recommendations For You ---")

            matched_product = recommendations.get("matched_product")
            if matched_product:
                print(f"✅ Matched: {matched_product['product_name']}")

            user_id = recommendations.get("user_id")
            if user_id:
                print(f"👤 Recommendations for User ID: {user_id}")

            similar_items = recommendations.get(
                "similar_recommendations",
                recommendations.get("recommendations", [])
            )

            if not similar_items:
                print("❌ No recommendations found.")
                return

            for item in similar_items:
                print(f"• {item['product_name']} (Score: {item['score']:.2f})")

            print("---------------------------------\n")
            break

# ==========================================================
# 🔹 SYSTEM PROMPT
# ==========================================================

SYSTEM_PROMPT = """
You are a professional and friendly E-commerce chatbot.
You help customers with:
- Product details
- Prices
- Offers
- Order tracking
- Return policy
- Payment methods
Speak clearly, briefly and politely like a real shopping assistant.
Always guide the user to buy products.
"""

# ==========================================================
# 🔹 MAIN CHAT LOOP
# ==========================================================

print("\n🛒 Welcome to Smart E-commerce Chatbot\n")

user_id = input("🔐 Enter your User ID to login: ")
print(f"\n✅ Login successful! Welcome User: {user_id}")
print("Type 'exit' to quit\n")

while True:
    user_input = input("Customer: ")

    if user_input.lower() == "exit":
        print("👋 Thank you for shopping with us!")
        break

    if "buy" in user_input.lower():
        print("\nHow would you like recommendations?")
        print("1️⃣ Recommend products using User ID")
        print("2️⃣ Recommend products based on what you want to buy\n")

        choice = input("Enter 1 or 2: ")

        if choice == "1":
            get_recommendations_from_user(user_id)
            continue

        elif choice == "2":
            statement = input("\n📝 What do you want to buy today? ")
            get_recommendations_from_keyword(statement)
            continue

    stream = ollama.chat(
        model="phi3",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_input}
        ],
        stream=True
    )

    print("Bot: ", end="")
    for chunk in stream:
        print(chunk["message"]["content"], end="", flush=True)
    print("\n")
