from predict_recipes import get_recommendations

def test():
    user_id = 675719
    ingredients = "chocolate"
    print(f"Testing recommendation for User {user_id} with ingredients: {ingredients}")
    
    try:
        recs = get_recommendations(user_id, ingredients)
        if recs.empty:
            print("No recommendations found.")
        else:
            print("Found recommendations:")
            print(recs[['recipe_id', 'title', 'pred_rating']].head())
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    test()
