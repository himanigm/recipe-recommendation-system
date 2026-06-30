
import pickle
import os
import sys

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'model', 'content_model.pkl')

if not os.path.exists(MODEL_PATH):
    print(f"Error: Model not found at {MODEL_PATH}")
    sys.exit(1)

print(f"Loading model from {MODEL_PATH}...")
with open(MODEL_PATH, 'rb') as f:
    data = pickle.load(f)

recipes = data['recipe_data']
print(f"Total recipes in model: {len(recipes)}")

# Check for new recipes
target_titles = [
    "Butter Chicken",
    "Chana Masala",
    "Palak Paneer",
    "Chicken Biryani",
    "Aloo Gobi"
]

found_count = 0
for r in recipes:
    if r['title'] in target_titles:
        print(f"Found: {r['title']} (ID: {r['recipe_id']})")
        found_count += 1

if found_count == len(target_titles):
    print("SUCCESS: All target Indian recipes found in the model.")
else:
    print(f"WARNING: Found {found_count}/{len(target_titles)} target recipes.")

# Basic recommendation check
tfidf = data['vectorizer']
tfidf_matrix = data['tfidf_matrix']

# Check dimensions
print(f"TF-IDF Matrix shape: {tfidf_matrix.shape}")
print(f"Recipe data length: {len(recipes)}")

assert tfidf_matrix.shape[0] == len(recipes), "Matrix rows show match recipe count"

print("Verification complete.")
