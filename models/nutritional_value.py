from sqlalchemy import DECIMAL
from . import db

class NutritionalValue(db.Model):
    """ Nutritional Values """

    __tablename__ = "nutritional_values"

    nutritional_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredients.ingredient_id'))
    nutrient_name = db.Column(db.String(50), nullable=False)
    amount = db.Column(DECIMAL(10, 2), nullable=False)
    unit = db.Column(db.String(10), nullable=False)
