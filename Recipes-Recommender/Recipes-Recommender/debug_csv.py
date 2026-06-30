
import pandas as pd
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Define path
base_dir = r"d:\project mca\Recipes-Recommender\Recipes-Recommender\Recipes-Recommender\recip-eeze-flask\recipeeze\datasets"
csv_path = os.path.join(base_dir, 'rr-recipes.csv')

print(f"Attempting to load: {csv_path}")

try:
    recipes_df = pd.read_csv(csv_path)
    print(f"Loaded successfully. Shape: {recipes_df.shape}")
    print(f"Columns: {recipes_df.columns.tolist()}")
    
    # Simulate cleaning
    def clean_ingredients(ingredient_str):
        if isinstance(ingredient_str, str):
            return ', '.join([i.strip().lower() for i in ingredient_str.split(',')])
        return ''

    recipes_df['clean_ingredients'] = recipes_df['ingredients'].apply(clean_ingredients)
    recipes_df = recipes_df[recipes_df['clean_ingredients'].str.strip() != ''].reset_index(drop=True)
    print(f"After cleaning shape: {recipes_df.shape}")

    if recipes_df.empty:
        print("Dataframe is empty after cleaning!")
    else:
        # Simulate recommendation
        vectorizer = TfidfVectorizer()
        ingredient_matrix = vectorizer.fit_transform(recipes_df['clean_ingredients'])
        
        user_ingredients = ['chocolate', 'milk']
        input_str = ', '.join(user_ingredients)
        input_vector = vectorizer.transform([input_str])
        
        cosine_sim = cosine_similarity(input_vector, ingredient_matrix)
        top_indices = cosine_sim[0].argsort()[::-1][:5]
        
        subset = recipes_df.iloc[top_indices][[
            'photo_url', 'title', 'ready_time', 'prep_time',
            'cook_time', 'directions', 'url', 'ingredients',
            'calories', 'fat', 'carbs', 'vitamins'
        ]]
        print("Recommendation successful. Top 5:")
        print(subset[['title', 'calories']])

except Exception as e:
    print(f"ERROR: {e}")
