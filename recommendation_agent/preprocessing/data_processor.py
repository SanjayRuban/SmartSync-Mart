import pandas as pd
from sklearn.preprocessing import LabelEncoder
from scipy.sparse import csr_matrix
import pickle
import os

class DataProcessor:
    def __init__(self, data_path):
        self.data_path = data_path
        
        # Dataframes
        self.orders_df = None
        self.products_df = None
        self.order_products_df = None

        # Encoded / processed
        self.user_encoder = LabelEncoder()
        self.product_encoder = LabelEncoder()
        self.user_item_matrix = None
        self.product_features = None

    # ==========================================================
    # 🔥 LOAD THE DATASET (INSTACART FORMAT)
    # ==========================================================
    def load_data(self):
        print("📌 Loading dataset...")

        # Load orders
        self.orders_df = pd.read_csv(os.path.join(self.data_path, "orders.csv"))
        print(f"   ✅ Loaded {len(self.orders_df)} orders")

        # Load products
        self.products_df = pd.read_csv(os.path.join(self.data_path, "products.csv"))
        print(f"   ✅ Loaded {len(self.products_df)} products")

        # Load prior and train
        print("   - Loading order_products__prior.csv...")
        prior_df = pd.read_csv(os.path.join(self.data_path, "order_products__prior.csv"))
        print(f"     ✅ Loaded {len(prior_df)} prior interactions")

        print("   - Loading order_products__train.csv...")
        train_df = pd.read_csv(os.path.join(self.data_path, "order_products__train.csv"))
        print(f"     ✅ Loaded {len(train_df)} train interactions")

        # Combine them
        self.order_products_df = pd.concat([prior_df, train_df])
        print(f"   🔥 Combined interactions = {len(self.order_products_df)} rows")

    # ==========================================================
    # 🔧 PREPROCESS DATA
    # ==========================================================
    def preprocess(self):
        print("\n🔧 Preprocessing data...")

        # -------------------------------
        # 1️⃣ Train label encoders
        # -------------------------------
        self.user_encoder.fit(self.orders_df["user_id"].unique())
        self.product_encoder.fit(self.products_df["product_id"].unique())

        print("   ✅ User & product encoders created")

        # -------------------------------
        # 2️⃣ Build user–item interaction matrix
        # -------------------------------
        print("   🔨 Building user-item matrix...")

        merged_df = pd.merge(self.order_products_df, self.orders_df, on="order_id")

        # encode
        merged_df["user_idx"] = self.user_encoder.transform(merged_df["user_id"])
        merged_df["product_idx"] = self.product_encoder.transform(merged_df["product_id"])

        # build sparse interaction matrix
        interactions = merged_df.groupby(["user_idx", "product_idx"]).size().reset_index(name="count")

        self.user_item_matrix = csr_matrix(
            (interactions["count"],
             (interactions["user_idx"], interactions["product_idx"])),
            shape=(len(self.user_encoder.classes_), len(self.product_encoder.classes_))
        )

        print(f"   ✅ User-item matrix shape = {self.user_item_matrix.shape}")

        # -------------------------------
        # 3️⃣ Create product features for content-based filtering
        # -------------------------------
        print("   🔨 Creating product features...")

        df = self.products_df.copy()
        df["aisle_encoded"] = LabelEncoder().fit_transform(df["aisle_id"])
        df["department_encoded"] = LabelEncoder().fit_transform(df["department_id"])

        self.product_features = df
        print("   ✅ Product features ready")

    # ==========================================================
    # GETTERS
    # ==========================================================
    def get_user_item_matrix(self):
        return self.user_item_matrix

    def get_product_features(self):
        return self.product_features

    def get_user_encoder(self):
        return self.user_encoder

    def get_product_encoder(self):
        return self.product_encoder

    # ==========================================================
    # SAVE / LOAD ENCODERS
    # ==========================================================
    def save_encoders(self, path):
        with open(os.path.join(path, "user_encoder.pkl"), "wb") as f:
            pickle.dump(self.user_encoder, f)
        with open(os.path.join(path, "product_encoder.pkl"), "wb") as f:
            pickle.dump(self.product_encoder, f)

    def load_encoders(self, path):
        with open(os.path.join(path, "user_encoder.pkl"), "rb") as f:
            self.user_encoder = pickle.load(f)
        with open(os.path.join(path, "product_encoder.pkl"), "rb") as f:
            self.product_encoder = pickle.load(f)
