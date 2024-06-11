from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

def connect_db(app):
    """Connect to database."""
    db.app = app
    db.init_app(app)

# Import models here to ensure they are registered with SQLAlchemy
from .user import User
from .recipe import Recipe
from .ingredient import Ingredient
from .recipe_ingredient import RecipeIngredient
from .nutritional_value import NutritionalValue
