# main.py

import os
import sys
import argparse

# Add the project root to the Python path to allow absolute imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from preprocessing.data_processor import DataProcessor
from models.collaborative_filtering import CollaborativeFiltering
from models.content_based import ContentBasedFiltering
from models.hybrid_model import HybridModel

def train_models(data_path, model_path):
    """
    Trains and saves the collaborative, content-based, and hybrid recommendation models.
    This function should be run when you have new data or want to retrain the models.
    """
    print("🚀 Starting the model training process...")
    
    # Initialize data processor
    print("📂 Initializing Data Processor...")
    data_processor = DataProcessor(data_path)
    print("✅ Data Processor initialized.")
    
    print("📥 Loading and preprocessing data...")
    data_processor.load_data()
    data_processor.preprocess()
    print("✅ Data loading and preprocessing complete.")

    # Save encoders for later use by the API
    print("💾 Saving encoders...")
    os.makedirs(model_path, exist_ok=True)
    data_processor.save_encoders(model_path)
    print(f"✅ Encoders saved to {model_path}")

    # Initialize collaborative filtering model
    print("🤖 Initializing Collaborative Filtering model...")
    user_item_matrix = data_processor.get_user_item_matrix()
    user_encoder = data_processor.get_user_encoder()
    product_encoder = data_processor.get_product_encoder()
    
    if user_item_matrix is None:
        print("❌ FATAL ERROR: user_item_matrix is None. Cannot train collaborative filtering.")
        print("   Please ensure you have 'order_products__prior.csv' or 'order_products__train.csv' in your data folder.")
        return # Stop execution

    collaborative_model = CollaborativeFiltering(user_item_matrix, user_encoder, product_encoder)
    print("✅ Collaborative Filtering model initialized.")

    print("🏋️ Training Collaborative Filtering model (ALS)...")
    collaborative_model.train_als(factors=20, regularization=0.01, iterations=30)
    print("✅ Collaborative Filtering model trained.")
    
    # Initialize content-based model
    print("🤖 Initializing Content-Based model...")
    product_features = data_processor.get_product_features()
    content_model = ContentBasedFiltering(product_features)
    print("✅ Content-Based model initialized.")

    print("🏋️ Training Content-Based model...")
    content_model.train()
    print("✅ Content-Based model trained.")

    # Initialize hybrid model
    print("🤖 Initializing Hybrid model...")
    hybrid_model = HybridModel(collaborative_model, content_model)
    print("✅ Hybrid model initialized.")

    # Save all trained models to disk
    print("💾 Saving all models...")
    collaborative_model.save_model(model_path)
    print("✅ Collaborative Filtering model saved.")
    
    content_model.save_model(model_path)
    print("✅ Content-Based model saved.")
    
    hybrid_model.save_model(model_path)
    print("✅ Hybrid model saved.")
    
    print("🎉 All models trained and saved successfully!")
    print("You can now start the Recommendation API server.")


def run_api(data_path, model_path, port=5000):
    """
    Initializes and runs the Recommendation API server.
    This service will listen for requests from the Sales Agent or API Gateway.
    """
    # Import the Flask app and initialization function from the API module
    from api.recommendation_api import app, initialize_models
    
    print("==============================================")
    print("🧠 STARTING RECOMMENDATION MICROSERVICE...")
    print("==============================================")
    print("This service provides intelligent product recommendations.")
    print(f"It will be accessible on port {port}.")
    
    # Load the pre-trained models into memory before starting the server
    try:
        initialize_models(data_path, model_path)
        print("\n✅ All models loaded successfully. API is ready to serve requests.")
    except Exception as e:
        print(f"\n❌ FATAL: Could not load models. Error: {e}")
        print("Please run 'python main.py --mode train' first to create the models.")
        sys.exit(1) # Exit with an error code

    # Start the Flask development server
    print(f"\n🚀 Starting Recommendation API Server on http://127.0.0.1:{port}...")
    app.run(host='0.0.0.0', port=port, debug=True)


def main():
    """
    Main entry point for the Recommendation Agent.
    Use command-line arguments to specify whether to train models or run the API.
    """
    parser = argparse.ArgumentParser(description='Retail Recommendation System - Recommendation Agent')
    parser.add_argument(
        '--mode', 
        choices=['train', 'api'], 
        default='api',
        help="Mode to run the application in: 'train' to train models, 'api' to start the API server."
    )
    parser.add_argument(
        '--data_path', 
        type=str, 
        default='data',
        help="Path to the directory containing CSV data files."
    )
    parser.add_argument(
        '--model_path', 
        type=str, 
        default='models',
        help="Path to the directory to save/load trained models."
    )
    parser.add_argument(
        '--port',
        type=int,
        default=5000,
        help="Port for the API server to run on (only used in 'api' mode)."
    )
    
    args = parser.parse_args()
    
    if args.mode == 'train':
        train_models(args.data_path, args.model_path)
    elif args.mode == 'api':
        run_api(args.data_path, args.model_path, args.port)

if __name__ == '__main__':
    main()