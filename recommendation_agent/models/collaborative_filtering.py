# models/collaborative_filtering.py

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix
import implicit
import pickle
import os

class CollaborativeFiltering:
    def __init__(self, user_item_matrix, user_encoder, product_encoder):
        self.user_item_matrix = user_item_matrix
        self.user_encoder = user_encoder
        self.product_encoder = product_encoder
        self.user_similarity = None
        self.item_similarity = None
        self.als_model = None
        
    def train_user_based(self):
        """Train user-based collaborative filtering"""
        # Compute user similarity matrix
        self.user_similarity = cosine_similarity(self.user_item_matrix)
        
    def train_item_based(self):
        """Train item-based collaborative filtering"""
        # Compute item similarity matrix
        self.item_similarity = cosine_similarity(self.user_item_matrix.T)
        
    def train_als(self, factors=20, regularization=0.01, iterations=30):
        """Train ALS model for implicit feedback"""
        # Convert to CSR matrix if not already
        if not isinstance(self.user_item_matrix, csr_matrix):
            self.user_item_matrix = csr_matrix(self.user_item_matrix)
            
        # Initialize and train ALS model
        self.als_model = implicit.als.AlternatingLeastSquares(
            factors=factors, 
            regularization=regularization, 
            iterations=iterations
        )
        self.als_model.fit(self.user_item_matrix)
        
    def recommend_for_user(self, user_id, n_recommendations=10, method='als'):
        """Generate recommendations for a user"""
        if method == 'user_based' and self.user_similarity is not None:
            return self._recommend_user_based(user_id, n_recommendations)
        elif method == 'item_based' and self.item_similarity is not None:
            return self._recommend_item_based(user_id, n_recommendations)
        elif method == 'als' and self.als_model is not None:
            return self._recommend_als(user_id, n_recommendations)
        else:
            raise ValueError(f"Method {method} not trained or not supported")
            
    def _recommend_user_based(self, user_id, n_recommendations):
        """User-based recommendation"""
        # Get user index
        try:
            user_idx = self.user_encoder.transform([user_id])[0]
        except ValueError:
            # New user, return popular items
            return self._recommend_popular_items(n_recommendations)
            
        # Get similar users
        user_similarities = self.user_similarity[user_idx]
        
        # Get items the user hasn't purchased
        user_items = self.user_item_matrix[user_idx].toarray().flatten()
        unrated_items = np.where(user_items == 0)[0]
        
        # Calculate scores for unrated items
        scores = np.zeros(len(unrated_items))
        for i, item_idx in enumerate(unrated_items):
            # Get users who have rated this item
            users_who_rated = self.user_item_matrix[:, item_idx].toarray().flatten() > 0
            
            # Calculate weighted sum of ratings
            if np.any(users_who_rated):
                scores[i] = np.sum(user_similarities[users_who_rated] * 
                                  self.user_item_matrix[users_who_rated, item_idx].toarray().flatten())
        
        # Get top recommendations
        top_item_indices = unrated_items[np.argsort(-scores)[:n_recommendations]]
        top_product_ids = self.product_encoder.inverse_transform(top_item_indices)
        
        return list(zip(top_product_ids, scores[np.argsort(-scores)[:n_recommendations]]))
        
    def _recommend_item_based(self, user_id, n_recommendations):
        """Item-based recommendation"""
        # Get user index
        try:
            user_idx = self.user_encoder.transform([user_id])[0]
        except ValueError:
            # New user, return popular items
            return self._recommend_popular_items(n_recommendations)
            
        # Get items the user has purchased
        user_items = self.user_item_matrix[user_idx].toarray().flatten()
        purchased_items = np.where(user_items > 0)[0]
        
        # Get items the user hasn't purchased
        unrated_items = np.where(user_items == 0)[0]
        
        # Calculate scores for unrated items
        scores = np.zeros(len(unrated_items))
        for i, item_idx in enumerate(unrated_items):
            # Get similarity to purchased items
            item_similarities = self.item_similarity[item_idx, purchased_items]
            
            # Calculate weighted sum of ratings
            scores[i] = np.sum(item_similarities * user_items[purchased_items])
        
        # Get top recommendations
        top_item_indices = unrated_items[np.argsort(-scores)[:n_recommendations]]
        top_product_ids = self.product_encoder.inverse_transform(top_item_indices)
        
        return list(zip(top_product_ids, scores[np.argsort(-scores)[:n_recommendations]]))
        
    def _recommend_als(self, user_id, n_recommendations):
        """ALS-based recommendation"""
        # Get user index
        try:
            user_idx = self.user_encoder.transform([user_id])[0]
        except ValueError:
            # New user, return popular items
            return self._recommend_popular_items(n_recommendations)
            
        # Get recommendations
        recommendations, scores = self.als_model.recommend(
            user_idx, 
            self.user_item_matrix[user_idx], 
            N=n_recommendations
        )
        
        # Convert back to product IDs
        top_product_ids = self.product_encoder.inverse_transform(recommendations)
        
        return list(zip(top_product_ids, scores))
        
    def _recommend_popular_items(self, n_recommendations):
        """Recommend popular items for new users"""
        # Calculate item popularity
        item_popularity = np.array(self.user_item_matrix.sum(axis=0)).flatten()
        
        # Get top items
        top_item_indices = np.argsort(-item_popularity)[:n_recommendations]
        top_product_ids = self.product_encoder.inverse_transform(top_item_indices)
        
        return list(zip(top_product_ids, item_popularity[top_item_indices]))
        
    def save_model(self, path):
        """Save the trained model"""
        model_data = {
            'user_similarity': self.user_similarity,
            'item_similarity': self.item_similarity,
            'als_model': self.als_model
        }
        
        with open(os.path.join(path, 'collaborative_filtering_model.pkl'), 'wb') as f:
            pickle.dump(model_data, f)
            
    def load_model(self, path):
        """Load a previously trained model"""
        with open(os.path.join(path, 'collaborative_filtering_model.pkl'), 'rb') as f:
            model_data = pickle.load(f)
            
        self.user_similarity = model_data['user_similarity']
        self.item_similarity = model_data['item_similarity']
        self.als_model = model_data['als_model']