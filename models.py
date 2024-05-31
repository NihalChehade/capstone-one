from enum import Enum
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DECIMAL
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

bcrypt = Bcrypt()


def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)


class User(db.Model):
    """User"""

    __tablename__ = "users"

    username = db.Column(db.String(20), 
                         primary_key=True)

    password = db.Column(db.Text, 
                         nullable=False)
    
    email = db.Column(db.String(50),
                      nullable = False,
                      unique = True)
    
    first_name = db.Column(db.String(30),
                           nullable = False)
    
    last_name = db.Column(db.String(30),
                          nullable = False)
    profile_image = db.Column(db.String(200), nullable=True, default='https://th.bing.com/th?id=OIP.Ze_F6AGBDQyYrlbNF7tCXAHaHa&w=250&h=250&c=8&rs=1&qlt=90&o=6&pid=3.1&rm=2') 

    bio = db.Column(db.Text, nullable=True)
    
    # comments = db.relationship('Comment', backref='user')

    # dietaryRestrictions = db.relationship('DietaryRestriction', secondary = 'users_dietary_restrictions', backref='user')
    
    recipes =db.relationship("Recipe", backref="user")
    
    
    
    # start_register
    @classmethod
    def signup(cls, username, pwd, email, fname, lname, bio, image):
        """Register user w/hashed password & return user."""

        hashed = bcrypt.generate_password_hash(pwd)
        # turn bytestring into normal (unicode utf8) string
        hashed_utf8 = hashed.decode("utf8")

        # return instance of user w/username and hashed pwd
        return cls(username=username, password=hashed_utf8, email=email, first_name=fname, last_name=lname, bio = bio, profile_image = image )
    # end_register

    # start_authenticate
    @classmethod
    def authenticate(cls, username, pwd):
        """Validate that user exists & password is correct.

        Return user if valid; else return False.
        """

        u = User.query.filter_by(username=username).first()

        if u and bcrypt.check_password_hash(u.password, pwd):
            # return user instance
            return u
        else:
            return False

class Recipe(db.Model):
    """recipe"""

    __tablename__ = "recipes"

    recipe_id = db.Column(db.Integer,
                    primary_key=True, 
                    autoincrement=True)
    
    username = db.Column(db.String(20),
                    db.ForeignKey('users.username'))
    
    title = db.Column(db.String(100),
                      nullable=False)
    
    description = db.Column(db.Text, nullable=False)

    instructions = db.Column(db.Text,
                             nullable= False)
    
    # votes = db.relationship("RecipeVote", backref="recipe")
    
    # nutritional_values = db.relationship('RecipeNutritionalValue', backref='recipe')

    # comments = db.relationship('Comment', backref='recipe')
    
    ingredients = db.relationship('Ingredient', secondary='recipes_ingredients', backref='recipe')
    
    recipes_ingredients_assoc = db.relationship('RecipeIngredient', backref= 'recipe')

# class DietaryRestriction(db.Model):  
#     """Dietary Restriction"""     
#     __tablename__ = 'dietary_restrictions'

#     restriction_id = db.Column(db.Integer, 
#                    primary_key=True, 
#                    autoincrement=True)
    
#     name = db.Column(db.String(30),
#                      nullable = False)
    
# class UserDietaryRestriction(db.Model):
#     """ User Dietary Restriction """

#     __tablename__ = 'users_dietary_restrictions'

#     username = db.Column(db.String(20),
#                     db.ForeignKey('users.username'),
#                     primary_key = True)
    
#     restriction_id = db.Column(db.Integer,
#                                db.ForeignKey('dietary_restrictions.restriction_id'),
#                                primary_key = True)

# class VoteEnum(Enum):
#     """Vote Enum"""
#     UPVOTE = 'upvote'
#     DOWNVOTE = 'downvote'


# class RecipeVote(db.Model):
#     """votes"""

#     __tablename__ = "recipe_votes"

#     vote_id = db.Column(db.Integer, 
#                    primary_key=True, 
#                    autoincrement=True)
    
#     recipe_id = db.Column(db.Integer,
#                     db.ForeignKey('recipes.recipe_id'))
    
#     username = db.Column(db.String(20),
#                     db.ForeignKey('users.username'))
    
#     voteType = db.Column(db.Enum(VoteEnum),
#                     default=VoteEnum.UPVOTE)
    

class Ingredient(db.Model):
    """ingredients"""

    __tablename__ = "ingredients"

    ingredient_id = db.Column(db.Integer, 
                   primary_key=True, 
                   autoincrement=True)
    
    name = db.Column(db.String(50),
                     nullable = False)
    
    image_url = db.Column(db.String(255))

    spoonacular_id = db.Column(db.Integer, nullable=True)
    
    nutritional_values = db.relationship('NutritionalValue', backref = 'ingredient', cascade="all, delete-orphan")
    
    recipes_ingredients_assoc = db.relationship('RecipeIngredient', backref= 'ingredient')


class RecipeIngredient(db.Model):
    """Recipes Ingredients"""

    __tablename__ = "recipes_ingredients"

    recipe_id = db.Column(db.Integer,
                          db.ForeignKey('recipes.recipe_id'),
                          primary_key =True)
    
    ingredient_id = db.Column(db.Integer,
                          db.ForeignKey('ingredients.ingredient_id'),
                          primary_key =True)
    
    quantity = db.Column(DECIMAL(10, 2),
                         nullable = False)
    
    unit = db.Column(db.String(50), nullable = False)

    


# class Comment(db.Model):
#     """comments"""

#     __tablename__ = "comments"

#     comment_id = db.Column(db.Integer,
#                            primary_key = True,
#                            autoincrement = True)
    
#     recipe_id = db.Column(db.Integer,
#                           db.ForeignKey('recipes.recipe_id'))
    
#     username = db.Column(db.String(20),
#                     db.ForeignKey('users.username'))
#     text = db.Column(db.Text,
#                      nullable = False)
    

class NutritionalValue(db.Model):
    """ Nutritional Values """
    __tablename__ = "nutritional_values"

    nutritional_id = db.Column(db.Integer,
                                primary_key=True,
                                  autoincrement=True)
    
    ingredient_id = db.Column(db.Integer,
                               db.ForeignKey('ingredients.ingredient_id'))
    
    nutrient_name = db.Column(db.String(50), nullable=False)

    amount = db.Column(DECIMAL(10, 2), nullable=False)

    unit = db.Column(db.String(10), nullable=False) 










