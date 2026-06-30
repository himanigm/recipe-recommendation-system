
import pandas as pd
import numpy as np
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Mimic app.py setup
BASE_DIR = r"d:\project mca\Recipes-Recommender\Recipes-Recommender\Web App"
RECIPES_PATH = os.path.join(BASE_DIR, 'datasets', 'rr-recipes.csv')

print(f"Loading from: {RECIPES_PATH}")

try:
    recipes_df = pd.read_csv(RECIPES_PATH)
    print(f"Columns: {recipes_df.columns.tolist()}")

    def clean_ingredients(ingredient_str):
        if isinstance(ingredient_str, str):
            return ', '.join([i.strip().lower() for i in ingredient_str.split(',')])
        return ''

    recipes_df['clean_ingredients'] = recipes_df['ingredients'].apply(clean_ingredients)
    recipes_df = recipes_df[recipes_df['clean_ingredients'].str.strip() != ''].reset_index(drop=True)
    
    print("Data loaded and cleaned.")
    
    # helper for recommend
    def recommend_recipes(user_ingredients, recipes_df, top_n=5):
        if recipes_df.empty:
            return pd.DataFrame()

        vectorizer = TfidfVectorizer()
        ingredient_matrix = vectorizer.fit_transform(recipes_df['clean_ingredients'])

        input_str = ', '.join(user_ingredients)
        input_vector = vectorizer.transform([input_str])

        cosine_sim = cosine_similarity(input_vector, ingredient_matrix)
        top_indices = cosine_sim[0].argsort()[::-1][:top_n]

        # This is where we suspect KeyError
        return recipes_df.iloc[top_indices][[
            'photo_url', 'title', 'ready_time', 'prep_time',
            'cook_time', 'directions', 'url', 'ingredients',
            'calories', 'fat', 'carbs', 'vitamins'
        ]]

    print("Attempting recommendation...")
    user_ingredients = ['chocolate', 'milk'] # mimic parse_ingredient_input
    result = recommend_recipes(user_ingredients, recipes_df)
    print("Recommendation Result:")
    print(result.head())

except Exception as e:
    print("CAUGHT EXCEPTION:")
    print(e)
    import traceback
    traceback.print_exc()
