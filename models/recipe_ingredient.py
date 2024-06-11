from sqlalchemy import DECIMAL
from . import db

class RecipeIngredient(db.Model):
    """Recipes Ingredients"""

    __tablename__ = "recipes_ingredients"

    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.recipe_id'), primary_key=True)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredients.ingredient_id'), primary_key=True)
    quantity = db.Column(DECIMAL(10, 2), nullable=False)
    unit = db.Column(db.String(50), nullable=False)
