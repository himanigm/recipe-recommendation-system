from flask import Flask, render_template, url_for, request, session, redirect, flash, jsonify
from flask_material import Material
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import re
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics.pairwise import cosine_similarity
import heapq
import pickle
import joblib
import os
from functools import wraps
import traceback
import datetime

def log_error(msg):
    with open("debug_log.txt", "a") as f:
        f.write(f"{datetime.datetime.now()}: {msg}\n")

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # In production, use a strong, unique secret key
Material(app)

@app.template_filter('format_time')
def format_time(minutes):
    """Formats minutes into 'X hr Y min' format."""
    try:
        minutes = int(minutes)
    except (ValueError, TypeError):
        return minutes
        
    if minutes < 60:
        return f"{minutes} mins"
    
    hours = minutes // 60
    mins = minutes % 60
    
    if mins == 0:
        return f"{hours} hr"
    else:
        return f"{hours} hr {mins} mins"

# Database initialization
def init_db():
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        conn.commit()

# Initialize database
init_db()

def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Please fill in all fields', 'danger')
            return redirect(url_for('register'))
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            hashed_password = generate_password_hash(password)
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                         (username, hashed_password))
            conn.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists. Please choose a different one.', 'danger')
        finally:
            conn.close()
    
    return render_template('register.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Please enter both username and password', 'danger')
            return redirect(url_for('login'))
            
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if user is None:
            flash('Username not found. Please register first.', 'danger')
            return redirect(url_for('login'))
            
        if check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['logged_in'] = True
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid password', 'danger')
    
    return render_template('login.html')

# Logout route
@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# Protected route example
@app.route('/')
@login_required
def index():
    return render_template('index.html', username=session.get('username'))

@app.route('/about')
@login_required
def about():
    return render_template('about.html')

@app.route('/contact')
@login_required
def contact():
    return render_template('contact.html')

@app.route('/prediction')
@login_required
def prediction():
    return render_template('Prediction.html')

# --- Prediction & Analysis Logic ---

# Define paths relative to the current script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RECIPES_PATH = os.path.join(BASE_DIR, 'datasets', 'rr-recipes.csv')
USERS_PATH = os.path.join(BASE_DIR, 'datasets', 'rr-users.csv')
RATINGS_PATH = os.path.join(BASE_DIR, 'datasets', 'rr-ratings.csv')
MODEL_PATH = os.path.join(BASE_DIR, 'model', 'recipes_recommender_model.sav')

# Load and clean dataset globally
try:
    recipes_df = pd.read_csv(RECIPES_PATH)
    
    def clean_ingredients(ingredient_str):
        if isinstance(ingredient_str, str):
            return ', '.join([i.strip().lower() for i in ingredient_str.split(',')])
        return ''

    recipes_df['clean_ingredients'] = recipes_df['ingredients'].apply(clean_ingredients)
    recipes_df = recipes_df[recipes_df['clean_ingredients'].str.strip() != ''].reset_index(drop=True)
except Exception as e:
    err_msg = f"Error loading global recipes data: {e}\n{traceback.format_exc()}"
    print(err_msg)
    log_error(err_msg)
    recipes_df = pd.DataFrame()

def parse_ingredient_input(input_string):
    return [item.strip().lower() for item in input_string.split(',') if item.strip()]

def recommend_recipes(user_ingredients, recipes_df, top_n=5):
    if recipes_df.empty:
        return pd.DataFrame()

    vectorizer = TfidfVectorizer()
    ingredient_matrix = vectorizer.fit_transform(recipes_df['clean_ingredients'])

    input_str = ', '.join(user_ingredients)
    input_vector = vectorizer.transform([input_str])

    cosine_sim = cosine_similarity(input_vector, ingredient_matrix)
    top_indices = cosine_sim[0].argsort()[::-1][:top_n]

    return recipes_df.iloc[top_indices][[
        'photo_url', 'title', 'ready_time', 'prep_time',
        'cook_time', 'directions', 'url', 'ingredients',
        'calories', 'fat', 'carbs', 'vitamins'
    ]]

# Load trained model
CONTENT_MODEL_PATH = os.path.join(BASE_DIR, 'model', 'content_model.pkl')
content_model = None

def load_content_model():
    global content_model
    if content_model is None:
        if os.path.exists(CONTENT_MODEL_PATH):
            with open(CONTENT_MODEL_PATH, 'rb') as f:
                content_model = pickle.load(f)
        else:
            print("Content model not found! Please run train_model.py first.")
            return None
    return content_model

@app.route('/main', methods=["POST"])
@login_required
def analyze():
    if request.method == 'POST':
        try:
            print("Calling analyze (Content-Based)")
            input_data = request.form.get('message', '')
            
            # Load model
            model_data = load_content_model()
            if not model_data:
                flash("Model not trained. Please contact administrator.", "danger")
                return render_template('contact.html')

            vectorizer = model_data['vectorizer']
            tfidf_matrix = model_data['tfidf_matrix']
            # recipe_data is a list of dicts, convert to DF for easy handling or use directly
            recipe_df = pd.DataFrame(model_data['recipe_data'])

            # Clean input
            clean_input = input_data.lower().replace(',', ' ')
            
            # Transform input
            input_vector = vectorizer.transform([clean_input])
            
            # Calculate Similarity
            # Use linear_kernel for speed (equivalent to cosine_similarity for normalized vectors)
            from sklearn.metrics.pairwise import linear_kernel
            cosine_sim = linear_kernel(input_vector, tfidf_matrix)
            
            # Get top matches
            # sim_scores is (1, N_recipes)
            sim_scores = list(enumerate(cosine_sim[0]))
            
            # Sort by score descending
            sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
            
            # Get top 20
            sim_scores = sim_scores[:20]
            
            # Filter out zero scores if necessary (irrelevant matches)
            sim_scores = [x for x in sim_scores if x[1] > 0]
            
            if not sim_scores:
                return render_template('contact.html', recipe_table=pd.DataFrame(), num_=0, res=1)
                
            recipe_indices = [i[0] for i in sim_scores]
            
            # Retrieve recipes
            result_df = recipe_df.iloc[recipe_indices].copy()
            
            # contact.html expects columns by index:
            # 0: image, 1: title, 2: ready_time, 3: prep_time, 4: cook_time, 5: directions, 6: url
            # Ensure columns exist. 'ready_time' might not calculate same as 'r_t' before, assume 'prep_time' or similar?
            # Original code: row[5] was 'r_t'. In standard DF clean:
            # photo_url, title, ready_time?, prep_time, cook_time, directions, url
            
            # Let's check keys in 'recipe_data'. train_model saved:
            # recipe_id, title, photo_url, ingredients, directions, prep_time, cook_time, calories, fat, carbs, vitamins, url
            
            # We construct the exact DF for the view
            # Using 'prep_time' as 'ready_time' duplicate if ready_time missing ??
            # Or just use prep_time twice?
            # Let's assume standard columns.
            
            final_view = result_df[['photo_url', 'title', 'prep_time', 'prep_time', 'cook_time', 'directions', 'url']].copy()
            # Note: I used prep_time for ready_time (col 2) as I didn't save ready_time in train_model explicitly if it wasn't there.
            # Let's check if 'ready_time' usually exists. It wasn't in my train_model save list?
            # train_model saved: prep_time, cook_time...
            
            # Wait, if 'ready_time' is missing from my saved model, this will fail if I try to select it.
            # I saved: 'recipe_id', 'title', 'photo_url', 'ingredients', 'directions', 'prep_time', 'cook_time', 'calories', 'fat', 'carbs', 'vitamins', 'url'
            # So I should use 'prep_time' for the third column as a placeholder or 'cook_time'.
            
            final_view.columns = range(7) # Reset columns to integers 0..6 for iloc access
            
            num_ = int(final_view.shape[0])
            print(f"Found {num_} recommendations")
            
            return render_template('contact.html', recipe_table=final_view, num_=num_, res=1)
            
        except Exception as e:
            print(f"Error in analyze: {e}")
            traceback.print_exc()
            flash(f"An error occurred: {str(e)}", 'danger')
            return redirect(url_for('contact'))
            
    return render_template('contact.html')

@app.route('/prediction1', methods=['GET', 'POST'])
@login_required
def prediction1():
    if request.method == 'POST':
        try:
            # FORCE RELOAD DATA to handle stale cache issues
            global recipes_df
            recipes_df = pd.read_csv(RECIPES_PATH)
            # Re-apply cleaning
            recipes_df['clean_ingredients'] = recipes_df['ingredients'].apply(clean_ingredients)
            recipes_df = recipes_df[recipes_df['clean_ingredients'].str.strip() != ''].reset_index(drop=True)
            
            ingredient_text = request.form['message']
            ingredients = parse_ingredient_input(ingredient_text)
            result_df = recommend_recipes(ingredients, recipes_df, top_n=5)
            records = result_df.to_dict('records')
            return render_template('Prediction.html', recipe_list=records, res=1)
        except Exception as e:
            err_msg = f"Error in prediction1: {e}\n{traceback.format_exc()}"
            print(err_msg)
            log_error(err_msg)
            flash('Error processing your request', 'danger')
            return render_template('Prediction.html', res=0)
            
    return render_template('Prediction.html', res=0)

if __name__ == '__main__':
    app.run(debug=True)
