import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle
import os
import sys

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, 'datasets', 'rr-recipes.csv')
MODEL_DIR = os.path.join(BASE_DIR, 'model')
MODEL_PATH = os.path.join(MODEL_DIR, 'content_model.pkl')

def train():
    print(f"Starting training process...")
    print(f"Looking for dataset at: {DATA_PATH}")
    
    if not os.path.exists(DATA_PATH):
        print(f"Error: Dataset not found at {DATA_PATH}")
        sys.exit(1)

    try:
        print("Loading dataset...")
        df = pd.read_csv(DATA_PATH)
        print(f"Loaded {len(df)} recipes.")
        
        # Cleaning
        print("Cleaning ingredient data...")
        # Simple cleaning: lowercase, remove nulls
        df['clean_ingredients'] = df['ingredients'].fillna('').astype(str).apply(lambda x: x.lower().replace(',', ' '))
        
        # TF-IDF Configurationa
        print("Training TF-IDF Vectorizer (Unigrams + Bigrams)...")
        tfidf = TfidfVectorizer(stop_words='english', ngram_range=(1, 2), min_df=2)
        
        tfidf_matrix = tfidf.fit_transform(df['clean_ingredients'])
        print(f"Model trained. Matrix shape: {tfidf_matrix.shape}")
        
        # Save artifacts
        if not os.path.exists(MODEL_DIR):
            os.makedirs(MODEL_DIR)
            print(f"Created model directory: {MODEL_DIR}")
            
        print(f"Saving model to {MODEL_PATH}...")
        with open(MODEL_PATH, 'wb') as f:
            pickle.dump({
                'vectorizer': tfidf,
                'tfidf_matrix': tfidf_matrix,
                # Save just the necessary columns to keep file size optimized, but include all display fields
                'recipe_data': df[['recipe_id', 'title', 'photo_url', 'ingredients', 'directions', 
                                 'prep_time', 'cook_time', 'calories', 'fat', 'carbs', 'vitamins', 'url']].to_dict('records')
            }, f)
            
        print("Training completed successfully!")
        
    except Exception as e:
        print(f"An error occurred during training: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    train()
