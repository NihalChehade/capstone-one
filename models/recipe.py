from . import db

class Recipe(db.Model):
    """recipe"""

    __tablename__ = "recipes"

    recipe_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    username = db.Column(db.String(20), db.ForeignKey('users.username'))

    title = db.Column(db.String(100), nullable=False)

    description = db.Column(db.Text, nullable=False)

    instructions = db.Column(db.Text, nullable=False)

    ingredients = db.relationship('Ingredient', secondary='recipes_ingredients', backref='recipe')

    recipes_ingredients_assoc = db.relationship('RecipeIngredient', backref='recipe')
