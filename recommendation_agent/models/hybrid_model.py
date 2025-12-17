# models/hybrid_model.py

import numpy as np
from .collaborative_filtering import CollaborativeFiltering
from .content_based import ContentBasedFiltering
import pickle
import os

class HybridModel:
    def __init__(self, collaborative_model, content_model, cf_weight=0.7):
        self.collaborative_model = collaborative_model
        self.content_model = content_model
        self.cf_weight = cf_weight  # Weight for collaborative filtering
        
    def recommend_for_user(self, user_id, user_purchase_history, n_recommendations=10):
        """Generate hybrid recommendations for a user"""
        # Get collaborative filtering recommendations
        cf_recommendations = self.collaborative_model.recommend_for_user(user_id, n_recommendations * 2)
        
        # Get content-based recommendations
        cb_recommendations = self.content_model.recommend_for_user(user_purchase_history, n_recommendations * 2)
        
        # Combine recommendations
        combined_scores = {}
        
        # Add collaborative filtering scores
        for product_id, score in cf_recommendations:
            combined_scores[product_id] = self.cf_weight * score
            
        # Add content-based scores
        for product_id, score in cb_recommendations:
            if product_id in combined_scores:
                combined_scores[product_id] += (1 - self.cf_weight) * score
            else:
                combined_scores[product_id] = (1 - self.cf_weight) * score
                
        # Sort by combined score and return top recommendations
        sorted_recommendations = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
        
        return sorted_recommendations[:n_recommendations]
        
    def recommend_similar_items(self, product_id, n_recommendations=10):
        """Find items similar to a given product using content-based approach"""
        return self.content_model.recommend_similar_items(product_id, n_recommendations)
        
    def save_model(self, path):
        """Save the hybrid model"""
        # Save collaborative filtering model
        self.collaborative_model.save_model(path)
        
        # Save content-based model
        self.content_model.save_model(path)
        
        # Save hybrid model parameters
        with open(os.path.join(path, 'hybrid_model_params.pkl'), 'wb') as f:
            pickle.dump({'cf_weight': self.cf_weight}, f)
            
    def load_model(self, path):
        """Load a previously trained hybrid model"""
        # Load collaborative filtering model
        self.collaborative_model.load_model(path)
        
        # Load content-based model
        self.content_model.load_model(path)
        
        # Load hybrid model parameters
        with open(os.path.join(path, 'hybrid_model_params.pkl'), 'rb') as f:
            params = pickle.load(f)
            self.cf_weight = params['cf_weight']