import pandas as pd
import pickle
import os
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors

def train():
    print("Loading datasets...")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dataset_dir = os.path.join(base_dir, 'recip-eeze-flask', 'recipeeze', 'datasets')
    model_dir = os.path.join(base_dir, 'recip-eeze-flask', 'recipeeze', 'model')
    
    ratings_path = os.path.join(dataset_dir, 'rr-ratings.csv')
    
    if not os.path.exists(ratings_path):
        print(f"Error: Ratings file not found at {ratings_path}")
        return

    ratings_df = pd.read_csv(ratings_path)
    
    print("Preparing sparse matrix (Item-based)...")
    
    # Mapping IDs to matrix indices
    # We want rows to be Items, columns to be Users
    
    # Get unique IDs
    unique_users = ratings_df['user'].unique()
    unique_items = ratings_df['item'].unique()
    
    # Create mappers
    user_mapper = {user: i for i, user in enumerate(unique_users)}
    item_mapper = {item: i for i, item in enumerate(unique_items)}
    
    # Inverse mappers
    user_inv_mapper = {i: user for i, user in enumerate(unique_users)}
    item_inv_mapper = {i: item for i, item in enumerate(unique_items)}
    
    # Map the dataframe
    user_indices = ratings_df['user'].map(user_mapper).values
    item_indices = ratings_df['item'].map(item_mapper).values
    ratings = ratings_df['rating'].values
    
    # Create CSR Matrix
    # Shape: (n_items, n_users)
    X = csr_matrix((ratings, (item_indices, user_indices)), 
                   shape=(len(unique_items), len(unique_users)))
    
    print(f"Matrix shape: {X.shape} with {X.nnz} ratings.")
    
    print("Training NearestNeighbors model (Cosine/Brute)...")
    # Metric='cosine' calculates 1 - cosine_similarity
    model = NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=20, n_jobs=-1)
    model.fit(X)
    
    # Package everything needed for inference
    artifact = {
        'model': model,
        'user_mapper': user_mapper,
        'item_mapper': item_mapper,
        'user_inv_mapper': user_inv_mapper,
        'item_inv_mapper': item_inv_mapper,
        'matrix': X
    }
    
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)
        
    # Using .pkl extension since it's a dictionary of objects check
    model_path = os.path.join(model_dir, 'recipes_recommender_model.pkl')
    print(f"Saving model artifact to {model_path}...")
    pickle.dump(artifact, open(model_path, 'wb'))
    print("Training completed successfully!")

if __name__ == "__main__":
    train()
