import pandas as pd
import pickle
import heapq
import os
import numpy as np

def load_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dataset_dir = os.path.join(base_dir, 'recip-eeze-flask', 'recipeeze', 'datasets')
    model_path = os.path.join(base_dir, 'recip-eeze-flask', 'recipeeze', 'model', 'recipes_recommender_model.pkl')
    
    print(f"Loading files from {dataset_dir}...")
    recipes_df = pd.read_csv(os.path.join(dataset_dir, 'rr-recipes.csv'))
    
    print(f"Loading model from {model_path}...")
    with open(model_path, 'rb') as f:
        artifact = pickle.load(f)
        
    return recipes_df, artifact

def predict_rating_for_item_user(item_idx, user_idx, model, X, k=20):
    """
    Predicts rating for a specific Item and User.
    Strategy: 
    1. Find K nearest neighbors of the ITEM.
    2. Filter neighbors to keep only those the USER has rated.
    3. Calculate weighted average of user's ratings.
    """
    # 1. Find neighbors for this item
    # Since X is (Item, User), we get neighbors of the row 'item_idx'
    
    # X[item_idx] is a sparse vector. 
    # Valid neighbors search
    item_vec = X[item_idx]
    
    # Get distances and indices of k neighbors
    distances, indices = model.kneighbors(item_vec, n_neighbors=k+1)
    
    # Flatten
    distances = distances.flatten()
    indices = indices.flatten()
    
    # First match is usually the item itself (dist=0), skip it
    # But checking if we filtered it out is safer.
    
    numerator = 0
    denominator = 0
    
    for i in range(len(indices)):
        neighbor_idx = indices[i]
        distance = distances[i] # This is cosine distance (1 - sim)
        
        # Skip self
        if neighbor_idx == item_idx:
            continue
            
        # Similarity = 1 - distance
        similarity = 1 - distance
        
        # If similarity is too low, maybe skip?
        if similarity <= 0:
            continue
            
        # did the user rate this neighbor item?
        # Check sparse matrix at (neighbor_idx, user_idx)
        # Note: accessing sparse matrix by index efficiently?
        # X is (items, users). 
        user_rating = X[neighbor_idx, user_idx]
        
        if user_rating > 0:
            numerator += similarity * user_rating
            denominator += similarity
            
    if denominator == 0:
        return 0 # Cannot predict
        
    return numerator / denominator

def get_recommendations(user_id, ingredient_list, N=20):
    recipes_df, artifact = load_data()
    
    model = artifact['model']
    item_mapper = artifact['item_mapper']
    item_inv_mapper = artifact['item_inv_mapper']
    user_mapper = artifact['user_mapper']
    X = artifact['matrix']
    
    # Check if user exists
    if user_id not in user_mapper:
        print(f"Warning: User ID {user_id} not found in training data. Making generic recommendations not supported yet.")
        return pd.DataFrame()
        
    user_idx = user_mapper[user_id]
    
    # Pre-process ingredients to filter candidates FIRST (Optimization)
    search_items = [item.strip() for item in ingredient_list.split(',')]
    
    # Filter DataFrame for candidates
    # We want recipes that contain ANY of the ingredients first? Or ALL? 
    # Usually "contains chocolate" implies containing at least chocolate.
    # Let's filter strict OR logic for now, or the user's "tofu" example implied simple search.
    
    # Construct regex
    regex_pattern = '|'.join([f"(?i){item}" for item in search_items])
    candidates = recipes_df[recipes_df['ingredients'].str.contains(regex_pattern, na=False)].copy()
    
    print(f"Found {len(candidates)} recipes matching ingredients.")
    
    if candidates.empty:
        return pd.DataFrame()
    
    predictions = []
    
    # Only predict for candidates
    for recipe_id in candidates['recipe_id']:
        # Check if item exists in model
        if recipe_id in item_mapper:
            item_idx = item_mapper[recipe_id]
            
            # Predict
            est_rating = predict_rating_for_item_user(item_idx, user_idx, model, X)
            
            if est_rating > 0:
                predictions.append((recipe_id, est_rating))
        else:
            # New item not in matrix
            pass
            
    # Sort predictions
    predictions.sort(key=lambda x: x[1], reverse=True)
    
    # Get Top N IDs
    top_recs = predictions[:N]
    
    if not top_recs:
        return pd.DataFrame()
        
    top_ids = [x[0] for x in top_recs]
    scores = {x[0]: x[1] for x in top_recs}
    
    result_df = recipes_df[recipes_df['recipe_id'].isin(top_ids)].copy()
    result_df['pred_rating'] = result_df['recipe_id'].map(scores)
    
    return result_df.sort_values('pred_rating', ascending=False)

def main():
    try:
        user_input = input("Enter User ID (e.g., 675719): ")
        if not user_input.strip():
            print("ID required.")
            return
        user_id = int(user_input)
        
        ingredients = input("Enter ingredients separated by commas (e.g., chocolate): ")
        
        recs = get_recommendations(user_id, ingredients)
        
        if recs.empty:
            print("No recommendations found matching your criteria.")
        else:
            print("\nTop Recommendations:")
            # Display readable columns
            cols = ['recipe_id', 'title', 'pred_rating', 'ingredients'] 
            print(recs[cols].to_string(index=False))
            
    except ValueError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
