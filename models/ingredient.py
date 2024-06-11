from . import db

class Ingredient(db.Model):
    """ingredients"""

    __tablename__ = "ingredients"

    ingredient_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    image_url = db.Column(db.String(255))
    spoonacular_id = db.Column(db.Integer, nullable=True)
    nutritional_values = db.relationship('NutritionalValue', backref='ingredient', cascade="all, delete-orphan")
    recipes_ingredients_assoc = db.relationship('RecipeIngredient', backref='ingredient')
