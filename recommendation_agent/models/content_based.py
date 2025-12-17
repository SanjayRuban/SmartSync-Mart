# models/content_based.py

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MinMaxScaler
from scipy.sparse import hstack
import pickle
import os

class ContentBasedFiltering:
    def __init__(self, product_features):
        self.product_features = product_features
        self.product_features_matrix = None
        self.tfidf_vectorizer = None
        self.nn_model = None
        self.product_to_idx_map = None
        
    def train(self, n_neighbors=20, retrain_nn=True):
        """
        Trains the content-based model using NearestNeighbors for efficiency.
        
        Args:
            n_neighbors (int): The number of neighbors to use for NearestNeighbors.
            retrain_nn (bool): If True, trains the NearestNeighbors model. 
                               If False, only recreates the feature matrix.
                               This is used when loading a pre-trained model.
        """
        print("   - 🏋️ Training Content-Based model (using NearestNeighbors)...")
        
        # Create a mapping from product_id to DataFrame index for quick lookups
        self.product_features = self.product_features.reset_index(drop=True)
        self.product_to_idx_map = pd.Series(self.product_features.index, index=self.product_features['product_id']).to_dict()
        
        # 1. Create TF-IDF features from product names
        print("   -   Creating TF-IDF features from product names...")
        product_names = self.product_features['product_name'].fillna('').values
        self.tfidf_vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
        product_tfidf_matrix = self.tfidf_vectorizer.fit_transform(product_names)
        print(f"   -   ✅ TF-IDF matrix created with shape: {product_tfidf_matrix.shape}")

        # 2. Prepare categorical features
        print("   -   Preparing categorical features (aisle, department)...")
        categorical_features = self.product_features[['aisle_id', 'department_id']].values
        scaler = MinMaxScaler()
        categorical_features_scaled = scaler.fit_transform(categorical_features)
        print(f"   -   ✅ Categorical features scaled with shape: {categorical_features_scaled.shape}")

        # 3. Combine all features into a single sparse matrix
        print("   -   Combining TF-IDF and categorical features...")
        self.product_features_matrix = hstack([product_tfidf_matrix, categorical_features_scaled])
        # --- THE FIX IS HERE ---
        # Convert the matrix to CSR format, which is efficient for row slicing
        self.product_features_matrix = self.product_features_matrix.tocsr()
        print(f"   -   ✅ Final feature matrix created in CSR format with shape: {self.product_features_matrix.shape}")

        # 4. Train the NearestNeighbors model (only if retrain_nn is True)
        if retrain_nn:
            print(f"   -   Training NearestNeighbors model to find top {n_neighbors} similar items...")
            self.nn_model = NearestNeighbors(n_neighbors=n_neighbors, algorithm='auto', metric='cosine')
            self.nn_model.fit(self.product_features_matrix)
            print("   - ✅ Content-Based model trained successfully!")
        else:
            print("   -   Skipping NN model training (retrain_nn is False).")
        
    def recommend_similar_items(self, product_id, n_recommendations=10):
        """Find items similar to a given product using the trained NN model."""
        if self.nn_model is None:
            print("Model not trained yet. Please call train() first.")
            return []
            
        try:
            # Get the internal index of the product
            product_idx = self.product_to_idx_map[product_id]
        except KeyError:
            print(f"Product ID {product_id} not found in the product catalog.")
            return []

        # Get the feature vector for the given product
        product_vector = self.product_features_matrix[product_idx]
        
        # Find the nearest neighbors
        # We ask for n_recommendations + 1 because the item itself will be the first neighbor
        distances, indices = self.nn_model.kneighbors(product_vector, n_neighbors=n_recommendations + 1)
        
        # The first result is the item itself, so we discard it
        similar_indices = indices.flatten()[1:]
        similarity_scores = 1 - distances.flatten()[1:]  # Convert distance to similarity

        # Get the product IDs for the similar items
        similar_product_ids = self.product_features.loc[similar_indices, 'product_id'].values
        
        return list(zip(similar_product_ids, similarity_scores))
        
    def recommend_for_user(self, user_purchase_history, n_recommendations=10):
        """Generate recommendations based on user's purchase history."""
        if not user_purchase_history:
            # No purchase history, return popular items (placeholder)
            return self._recommend_popular_items(n_recommendations)
            
        # Get recommendations for each item in the user's history
        all_recs = {}
        for product_id in user_purchase_history:
            similar_items = self.recommend_similar_items(product_id, n_recommendations * 2)
            for rec_id, score in similar_items:
                if rec_id not in user_purchase_history: # Don't recommend what they already bought
                    if rec_id in all_recs:
                        all_recs[rec_id] += score
                    else:
                        all_recs[rec_id] = score
        
        # Sort by combined score and return top N
        sorted_recs = sorted(all_recs.items(), key=lambda x: x[1], reverse=True)
        return sorted_recs[:n_recommendations]
        
    def _recommend_popular_items(self, n_recommendations):
        """Recommend popular items (placeholder implementation)."""
        # In a real system, this would be based on actual purchase frequency.
        # For now, we'll just return the first N items.
        top_product_ids = self.product_features.head(n_recommendations)['product_id'].values
        return list(zip(top_product_ids, [1.0] * n_recommendations))
        
    def save_model(self, path):
        """Save the trained model components."""
        model_data = {
            'nn_model': self.nn_model,
            'tfidf_vectorizer': self.tfidf_vectorizer,
            'product_to_idx_map': self.product_to_idx_map
        }
        
        with open(os.path.join(path, 'content_based_model.pkl'), 'wb') as f:
            pickle.dump(model_data, f)
            
    def load_model(self, path):
        """Load a previously trained model."""
        with open(os.path.join(path, 'content_based_model.pkl'), 'rb') as f:
            model_data = pickle.load(f)
            
        self.nn_model = model_data['nn_model']
        self.tfidf_vectorizer = model_data['tfidf_vectorizer']
        self.product_to_idx_map = model_data['product_to_idx_map']