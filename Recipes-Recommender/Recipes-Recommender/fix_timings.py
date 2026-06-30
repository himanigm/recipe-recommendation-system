
import pandas as pd
import numpy as np
import os

# Define path to the ACTIVE dataset
base_dir = r"d:\project mca\Recipes-Recommender\Recipes-Recommender\Web App\datasets"
csv_path = os.path.join(base_dir, 'rr-recipes.csv')

print(f"Reading from {csv_path}...")
df = pd.read_csv(csv_path)

# Check counts before
zeros_prep = (df['prep_time'] == 0).sum()
zeros_cook = (df['cook_time'] == 0).sum()
print(f"Zeros before - Prep: {zeros_prep}, Cook: {zeros_cook}")

# Random generators
def get_random_prep():
    return np.random.randint(5, 45) # 5 to 45 mins

def get_random_cook():
    return np.random.randint(10, 90) # 10 to 90 mins

# Update columns where value is 0
mask_prep = df['prep_time'] == 0
mask_cook = df['cook_time'] == 0

df.loc[mask_prep, 'prep_time'] = df.loc[mask_prep].apply(lambda x: get_random_prep(), axis=1)
df.loc[mask_cook, 'cook_time'] = df.loc[mask_cook].apply(lambda x: get_random_cook(), axis=1)

# Recalculate ready_time = prep + cook
df['ready_time'] = df['prep_time'] + df['cook_time']

# Check counts after
zeros_prep_after = (df['prep_time'] == 0).sum()
zeros_cook_after = (df['cook_time'] == 0).sum()
print(f"Zeros after - Prep: {zeros_prep_after}, Cook: {zeros_cook_after}")

# Save
df.to_csv(csv_path, index=False)
print("Successfully updated timings!")
