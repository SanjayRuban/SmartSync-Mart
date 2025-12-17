import firebase_admin
from firebase_admin import credentials, firestore
import time
import os
import sys

# ==========================================================
# 🔥 FIREBASE INIT
# ==========================================================

cred = credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# ==========================================================
# 🔥 LOAD RECOMMENDATION SYSTEM (SAME AS YOUR FLASK API)
# ==========================================================

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from preprocessing.data_processor import DataProcessor
from models.collaborative_filtering import CollaborativeFiltering
from models.content_based import ContentBasedFiltering
from models.hybrid_model import HybridModel

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_path = os.path.join(project_root, "data")
model_path = os.path.join(project_root, "models")

print("🔁 Initializing Recommendation Models (Firebase Listener)...")

data_processor = DataProcessor(data_path)
data_processor.load_data()
data_processor.preprocess()
products_df = data_processor.get_product_features()

user_item_matrix = data_processor.get_user_item_matrix()
user_encoder = data_processor.get_user_encoder()
product_encoder = data_processor.get_product_encoder()

collaborative_model = CollaborativeFiltering(
    user_item_matrix, user_encoder, product_encoder
)
collaborative_model.load_model(model_path)

content_model = ContentBasedFiltering(products_df)
content_model.load_model(model_path)
content_model.train(retrain_nn=False)

hybrid_model = HybridModel(collaborative_model, content_model)
hybrid_model.load_model(model_path)

print("✅ Firebase Recommendation Listener Started")

# ==========================================================
# 🔁 FIREBASE REQUEST PROCESSOR LOOP
# ==========================================================

while True:
    requests_ref = db.collection("requests").where("status", "==", "pending").stream()

    for req in requests_ref:
        data = req.to_dict()
        request_type = data.get("type")

        print("Processing:", data)

        # ======================================================
        # ✅ KEYWORD BASED RECOMMENDATION (OPTION 2)
        # ======================================================
        if request_type == "keyword":
            keyword = data["keyword"].strip().lower()

            matches = products_df[
                products_df['product_name'].str.lower().str.contains(keyword, na=False)
            ]

            if matches.empty:
                result = {"message": "No product found"}
            else:
                top_product = matches.iloc[0].to_dict()
                top_product_id = top_product['product_id']

                similar_items = hybrid_model.recommend_similar_items(top_product_id, 10)

                detailed_similar = []
                for pid, score in similar_items:
                    product_details = products_df[
                        products_df['product_id'] == pid
                    ].iloc[0].to_dict()
                    product_details['score'] = float(score)
                    detailed_similar.append(product_details)

                result = {
                    "keyword": keyword,
                    "matched_product": top_product,
                    "similar_recommendations": detailed_similar
                }

        # ======================================================
        # ✅ USER ID BASED RECOMMENDATION (OPTION 1 — SAME AS FLASK)
        # ======================================================
        elif request_type == "user":
            user_id = int(data["user_id"])
            n = int(data.get("n", 10))

            user_purchase_history = []

            recommendations = hybrid_model.recommend_for_user(
                user_id, user_purchase_history, n
            )

            detailed_recommendations = []
            for product_id, score in recommendations:
                product_details = products_df[
                    products_df['product_id'] == product_id
                ].iloc[0].to_dict()
                product_details['score'] = float(score)
                detailed_recommendations.append(product_details)

            result = {
                "user_id": user_id,
                "recommendations": detailed_recommendations
            }

        else:
            result = {"message": "Invalid request type"}

        # ======================================================
        # ✅ STORE RESPONSE & MARK AS DONE
        # ======================================================
        db.collection("responses").document(req.id).set(result)
        db.collection("requests").document(req.id).update({"status": "done"})

    time.sleep(1)