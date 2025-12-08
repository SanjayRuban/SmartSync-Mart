import ollama
import pandas as pd

# ---------- LOAD CSV ----------
df = pd.read_csv("matched_250_products.csv")
product_list = df["product_name"].str.lower().tolist()

# ---------- SYSTEM PROMPT ----------
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

# ---------- LOGIN ----------
print("\n🛒 Welcome to Smart E-commerce Chatbot\n")
user_id = input("🔐 Enter your User ID to login: ")
print(f"\n✅ Login successful! Welcome User: {user_id}")
print("Type 'exit' to quit\n")

# ---------- MAIN LOOP ----------
while True:
    user = input("Customer: ")

    if user.lower() == "exit":
        print("👋 Thank you for shopping with us!")
        break

    # ---------- BUY INTENT ----------
    if "buy" in user.lower():
        print("\nHow would you like recommendations?")
        print("1️⃣ Recommend products using User ID")
        print("2️⃣ Recommend products using Past Purchase Statement\n")

        choice = input("Enter 1 or 2: ")

        # ✅ OPTION 1 — USER ID BASED
        if choice == "1":
            print(f"\n✅ Recommendations for User ID: {user_id}")
            print("🛍️ (Demo) Products recommended using your profile.\n")
            continue

        # ✅ OPTION 2 — STATEMENT BASED USING OLLAMA
        elif choice == "2":
            statement = input("\n📝 What do you want to buy today? ")

            # ---------- OLLAMA KEYWORD EXTRACTION ----------
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

            print(f"\n🔍 Extracted Keyword from Ollama: {extracted_keyword}")

            # ---------- MATCH WITH CSV ----------
            matched_product = None
            for product in product_list:
                if product in extracted_keyword or extracted_keyword in product:
                    matched_product = product
                    break

            if matched_product:
                print(f"\n✅ Matched Product from CSV: {matched_product}")

            else:
                print("\n❌ No matching product found in CSV.\n")

            continue

    # ---------- NORMAL CHAT ----------
    stream = ollama.chat(
        model="phi3",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user}
        ],
        stream=True
    )

    print("Bot: ", end="")
    for chunk in stream:
        print(chunk["message"]["content"], end="", flush=True)
    print("\n")
