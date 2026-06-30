
import csv
import os

# Define the data
recipes = [
    {
        "recipe_id": 30000,
        "title": "Butter Chicken",
        "prep_time": 30,
        "cook_time": 40,
        "ready_time": 70,
        "ingredients": "chicken,butter,tomato puree,cream,garam masala,fenugreek,ginger,garlic,cumin,coriander,chili powder,yogurt",
        "directions": "Marinate chicken in yogurt and spices. Cook in tandoor or oven. Simmer tomato puree with butter and spices. Add cream and chicken. Cook until tender.",
        "url": "https://www.allrecipes.com/recipe/butter-chicken",
        "photo_url": "https://images.media-allrecipes.com/userphotos/560x315/butter-chicken.jpg",
        "calories": 450,
        "fat": 25,
        "carbs": 10,
        "vitamins": "Vitamin A, Calcium"
    },
    {
        "recipe_id": 30001,
        "title": "Chana Masala",
        "prep_time": 15,
        "cook_time": 30,
        "ready_time": 45,
        "ingredients": "chickpeas,onion,tomato,ginger,garlic,cumin,coriander,turmeric,chili powder,garam masala,lemon",
        "directions": "Saute spices with onion, ginger, and garlic. Add tomatoes and cook until soft. Add chickpeas and water. Simmer until thickened. Finish with lemon juice.",
        "url": "https://www.allrecipes.com/recipe/chana-masala",
        "photo_url": "https://images.media-allrecipes.com/userphotos/560x315/chana-masala.jpg",
        "calories": 280,
        "fat": 8,
        "carbs": 45,
        "vitamins": "Iron, Vitamin C"
    },
    {
        "recipe_id": 30002,
        "title": "Palak Paneer",
        "prep_time": 20,
        "cook_time": 20,
        "ready_time": 40,
        "ingredients": "spinach,paneer,onion,tomato,ginger,garlic,cumin,garam masala,cream,turmeric,chili",
        "directions": "Blanch spinach and puree. Saute cumin, onion, ginger, garlic. Add tomatoes and spices. Add spinach puree and cream. Simmer. Add paneer cubes.",
        "url": "https://www.allrecipes.com/recipe/palak-paneer",
        "photo_url": "https://images.media-allrecipes.com/userphotos/560x315/palak-paneer.jpg",
        "calories": 320,
        "fat": 22,
        "carbs": 12,
        "vitamins": "Vitamin A, Iron, Calcium"
    },
    {
        "recipe_id": 30003,
        "title": "Chicken Biryani",
        "prep_time": 40,
        "cook_time": 60,
        "ready_time": 100,
        "ingredients": "basmati rice,chicken,yogurt,onion,tomato,ginger,garlic,mint,coriander,saffron,biryani masala,ghee",
        "directions": "Marinate chicken. Par-boil rice with whole spices. Layer chicken and rice in a pot. Top with saffron milk, mint, coriander, and ghee. Cook on low heat (dum).",
        "url": "https://www.allrecipes.com/recipe/chicken-biryani",
        "photo_url": "https://images.media-allrecipes.com/userphotos/560x315/chicken-biryani.jpg",
        "calories": 600,
        "fat": 20,
        "carbs": 70,
        "vitamins": "Vitamin B12"
    },
    {
        "recipe_id": 30004,
        "title": "Aloo Gobi",
        "prep_time": 15,
        "cook_time": 25,
        "ready_time": 40,
        "ingredients": "potato,cauliflower,onion,tomato,ginger,cumin,turmeric,coriander,chili powder,garam masala,cilantro",
        "directions": "Fry potatoes and cauliflower until golden. Saute cumin, onion, ginger. Add tomatoes and spices. Add fried vegetables and steam until tender. Garnish with cilantro.",
        "url": "https://www.allrecipes.com/recipe/aloo-gobi",
        "photo_url": "https://images.media-allrecipes.com/userphotos/560x315/aloo-gobi.jpg",
        "calories": 210,
        "fat": 9,
        "carbs": 28,
        "vitamins": "Vitamin C, Vitamin K"
    },
    {
        "recipe_id": 30005,
        "title": "Naan",
        "prep_time": 120,
        "cook_time": 10,
        "ready_time": 130,
        "ingredients": "flour,yeast,yogurt,milk,sugar,salt,baking powder,ghee,nigella seeds",
        "directions": "Mix dough ingredients and knead. Let rise until doubled. Divide into balls and roll out. Cook in tandoor or hot skillet. Brush with butter/ghee.",
        "url": "https://www.allrecipes.com/recipe/naan",
        "photo_url": "https://images.media-allrecipes.com/userphotos/560x315/naan.jpg",
        "calories": 260,
        "fat": 6,
        "carbs": 45,
        "vitamins": "Calcium"
    },
    {
        "recipe_id": 30006,
        "title": "Masoor Dal",
        "prep_time": 10,
        "cook_time": 30,
        "ready_time": 40,
        "ingredients": "red lentils,onion,tomato,ginger,garlic,turmeric,mustard seeds,cumin,curry leaves,chili",
        "directions": "Boil lentils with turmeric until soft. Temper mustard seeds, cumin, curry leaves, onion, ginger, garlic, and chili in oil. Mix with dal. Simmer.",
        "url": "https://www.allrecipes.com/recipe/masoor-dal",
        "photo_url": "https://images.media-allrecipes.com/userphotos/560x315/masoor-dal.jpg",
        "calories": 230,
        "fat": 4,
        "carbs": 38,
        "vitamins": "Iron, Folate"
    },
    {
        "recipe_id": 30007,
        "title": "Samosas",
        "prep_time": 45,
        "cook_time": 30,
        "ready_time": 75,
        "ingredients": "flour,potato,peas,cumin,coriander,garam masala,chili,ginger,oil,salt,ajwain",
        "directions": "Make dough with flour, oil, salt, ajwain. Make filling with boiled potatoes, peas, spices. Roll dough, stuff with filling, seal. Deep fry until golden.",
        "url": "https://www.allrecipes.com/recipe/samosas",
        "photo_url": "https://images.media-allrecipes.com/userphotos/560x315/samosas.jpg",
        "calories": 300,
        "fat": 15,
        "carbs": 35,
        "vitamins": "Vitamin C"
    },
    {
        "recipe_id": 30008,
        "title": "Rogan Josh",
        "prep_time": 30,
        "cook_time": 90,
        "ready_time": 120,
        "ingredients": "lamb,yogurt,onion,garlic,ginger,kashmiri chili,fennel,cardamom,clove,cinnamon,oil",
        "directions": "Brown meat in oil. Saute whole spices and onion paste. Add ground spices and yogurt. Cook until oil separates. Add meat and water. Simmer until tender.",
        "url": "https://www.allrecipes.com/recipe/rogan-josh",
        "photo_url": "https://images.media-allrecipes.com/userphotos/560x315/rogan-josh.jpg",
        "calories": 480,
        "fat": 28,
        "carbs": 8,
        "vitamins": "Iron, Zinc"
    },
    {
        "recipe_id": 30009,
        "title": "Tandoori Chicken",
        "prep_time": 20,
        "cook_time": 40,
        "ready_time": 60,
        "ingredients": "chicken,yogurt,lemon,ginger,garlic,kashmiri chili,turmeric,garam masala,mustard oil,salt",
        "directions": "Make incisions in chicken. Marinate with lime, salt, chili. Second marinade with yogurt and spices. Grill or bake at high heat until charred and cooked.",
        "url": "https://www.allrecipes.com/recipe/tandoori-chicken",
        "photo_url": "https://images.media-allrecipes.com/userphotos/560x315/tandoori-chicken.jpg",
        "calories": 350,
        "fat": 18,
        "carbs": 5,
        "vitamins": "Vitamin B6"
    }
]

file_path = r"d:\project mca\Recipes-Recommender\Recipes-Recommender\Web App\datasets\rr-recipes.csv"

# Append to CSV
with open(file_path, 'a', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=[
        'recipe_id', 'title', 'prep_time', 'cook_time', 'ready_time', 
        'ingredients', 'directions', 'url', 'photo_url', 
        'calories', 'fat', 'carbs', 'vitamins'
    ])
    # writer.writeheader() # file already exists
    for recipe in recipes:
        writer.writerow(recipe)

print(f"Successfully added {len(recipes)} recipes to {file_path}")
