import logging
import requests
from models import db, User, Recipe, Ingredient, NutritionalValue, RecipeIngredient
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_BASE_URL = "https://api.spoonacular.com"

SPOONACULAR_API_KEY = os.environ.get('SPOONACULAR_API_KEY')

SPECIFIED_NUTRIENTS = [
    "Calories", 
    "Fat", 
    "Saturated Fat", 
    "Cholesterol", 
    "Sodium", 
    "Carbohydrates",
    "Fiber",
    "Sugar",
    "Protein"
]

# Function to call the API
def get_ingredient_info(spoonacular_id, quantity, unit):
    try:
        response = requests.get(f"{API_BASE_URL}/food/ingredients/{spoonacular_id}/information?apiKey={SPOONACULAR_API_KEY}&amount={quantity}&unit={unit}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching ingredient info for ID {spoonacular_id}: {e}")
        return None

# Function to process ingredient information
def process_ingredient_info(ingredient_info):
    if ingredient_info:
        
        name = ingredient_info.get('name')
        spoonacular_id = ingredient_info.get('id')
        image_url = ingredient_info.get('image', '')
        nutrients = ingredient_info.get('nutrition', {}).get('nutrients', [])
        
        processed_nutrients = [
            {
                'name': nutrient['name'],
                'amount': nutrient.get('amount', 0),
                'unit': nutrient.get('unit', '')
            }
            for nutrient in nutrients if nutrient['name'] in SPECIFIED_NUTRIENTS
        ]
        return name, spoonacular_id, image_url, processed_nutrients
    return None, None, None, []

# Function to store ingredient and its nutritional values in the database
def store_ingredient(name, spoonacular_id, image_url, nutrients):
    existing_ingredient = Ingredient.query.filter_by(name=name).first()
    if existing_ingredient:
        ingredient_id = existing_ingredient.ingredient_id
    else:
        new_ingredient = Ingredient(name=name, spoonacular_id=spoonacular_id, image_url=image_url)
        db.session.add(new_ingredient)
        db.session.flush()
        ingredient_id = new_ingredient.ingredient_id

        for nutrient in nutrients:
            new_nutritional_value = NutritionalValue(
                ingredient_id=ingredient_id,
                nutrient_name=nutrient['name'],
                amount=nutrient['amount'],
                unit=nutrient['unit']
            )
            db.session.add(new_nutritional_value)

    return ingredient_id

def get_user_by_username(username):
    return User.query.filter_by(username=username).first()

def get_user_by_email(email):
    return User.query.filter_by(email=email).first()

def create_user(username, password, email, first_name, last_name, bio, profile_image):
    user = User.signup(username, password, email, first_name, last_name, bio=bio, image=profile_image)
    db.session.add(user)
    db.session.commit()
    return user

def authenticate_user(username, password):
    return User.authenticate(username, password)

def get_recipe_by_id(recipe_id):
    return Recipe.query.get_or_404(recipe_id)

def create_recipe(username, title, description, instructions):
    new_recipe = Recipe(username=username, title=title, description=description, instructions=instructions)
    db.session.add(new_recipe)
    db.session.flush()  # Ensure the recipe ID is available for ingredients
    return new_recipe

def create_recipe_ingredient(recipe_id, ingredient_id, quantity, unit):
    recipe_ingredient = RecipeIngredient(
        recipe_id=recipe_id,
        ingredient_id=ingredient_id,
        quantity=quantity,
        unit=unit
    )
    db.session.add(recipe_ingredient)

def commit_session():
    db.session.commit()

def calculate_nutritional_values(recipe):
    nutritional_totals = {'units': {}}

    for recipe_ingredient in recipe.recipes_ingredients_assoc:
        ingredient = recipe_ingredient.ingredient
        
        for nutritional_value in ingredient.nutritional_values:
            nutrient_name = nutritional_value.nutrient_name
            total_amount = nutritional_value.amount

            if nutrient_name in nutritional_totals:
                nutritional_totals[nutrient_name] += total_amount
            else:
                nutritional_totals[nutrient_name] = total_amount
                nutritional_totals['units'][nutrient_name] = nutritional_value.unit

    return nutritional_totals
