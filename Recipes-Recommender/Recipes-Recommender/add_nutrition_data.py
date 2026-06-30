import pandas as pd
import numpy as np
import os

# Define path
base_dir = r"d:\project mca\Recipes-Recommender\Recipes-Recommender\Web App\datasets"
csv_path = os.path.join(base_dir, 'rr-recipes.csv')

print(f"Reading from {csv_path}...")
df = pd.read_csv(csv_path)

# Check if columns already exist
if 'calories' not in df.columns:
    print("Generating mock nutritional data...")
    # Generate random but reasonable values
    np.random.seed(42) # For reproducibility
    
    # Calories: 150 - 800 kcal
    df['calories'] = np.random.randint(150, 801, df.shape[0])
    
    # Fat: 5 - 40g
    df['fat'] = np.random.randint(5, 41, df.shape[0])
    
    # Carbs: 10 - 100g
    df['carbs'] = np.random.randint(10, 101, df.shape[0])
    
    # Vitamins: Random selection of vitamins
    vitamins_list = ['Vitamin A', 'Vitamin C', 'Calcium', 'Iron', 'Vitamin D', 'Vitamin B12']
    
    def get_random_vitamins():
        num_vits = np.random.randint(1, 4)
        vits = np.random.choice(vitamins_list, num_vits, replace=False)
        return ", ".join(vits)
        
    df['vitamins'] = [get_random_vitamins() for _ in range(df.shape[0])]
    
    # Save back to CSV
    df.to_csv(csv_path, index=False)
    print(f"Successfully added nutritional columns to {csv_path}")
    print(df[['title', 'calories', 'fat', 'carbs', 'vitamins']].head())
else:
    print("Nutritional columns already exist.")
