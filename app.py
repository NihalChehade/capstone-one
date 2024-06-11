from flask import Flask, render_template, redirect, session, flash, request, current_app, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db
from models.user import User
from models.recipe import Recipe
from models.ingredient import Ingredient
from models.recipe_ingredient import RecipeIngredient
from models.nutritional_value import NutritionalValue
from forms import SignUpForm, LoginForm, RecipeForm, IngredientForm
import os
import secrets
from PIL import Image
from flask_wtf.csrf import generate_csrf
from dotenv import load_dotenv
import db_operations as db_ops

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Ensure database URL is available
db_url = os.environ.get('DATABASE_URL', 'postgresql://njaicrqz:gyXNe8QlCSAVE4qiBMCTR0tin6LTCYKC@bubble.db.elephantsql.com/njaicrqz')
if not db_url:
    raise ValueError("DATABASE_URL is not set in the environment variables.")

app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = os.environ.get('SECRET_KEY', 'aaaabbbbcccc1123333')
app.config['WTF_CSRF_TIME_LIMIT'] = 120

connect_db(app)

with app.app_context():
    db.create_all()


toolbar = DebugToolbarExtension(app)

@app.route('/')
def boarding():
    return render_template('index.html')

def save_profile_image(form_image):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_image.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)

    # Resize image
    output_size = (125, 125)
    img = Image.open(form_image)
    img.thumbnail(output_size)
    img.save(picture_path)

    return picture_fn

@app.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignUpForm()
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        bio = form.bio.data
        profile_image = form.profile_image.data

        if db_ops.get_user_by_username(username):
            flash('Username already exists please choose a new username!', 'danger')
            return redirect("/signup")
        
        if db_ops.get_user_by_email(email):
            flash('Email already in use please choose a new one!', 'danger')
            return redirect("/signup")
        
        if form.profile_image.data:
            profile_image = save_profile_image(form.profile_image.data)
        else:
            profile_image = 'default_profile.png'

        user = db_ops.create_user(username, password, email, first_name, last_name, bio, profile_image)
        session["username"] = user.username
        flash("Welcome on board!!", "success")
        return redirect("/")

    return render_template("signup.html", form=form)
    
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = db_ops.authenticate_user(username, password)

        if user:
            session["username"] = user.username 
            flash("Login successful", "success")
            return redirect("/")
        else:
            flash("Invalid username or password", "danger")
            form.username.errors = ["username or password is incorrect!"]

    return render_template("login.html", form=form)
 
@app.route("/logout")
def logout():
    session.pop("username")
    flash("You have been logged out", "danger")
    return redirect("/")

@app.route("/users/<username>")
def show_user(username):
    if 'username' not in session:
        flash('You need to be logged in to view your profile.', 'danger')
        return redirect('/login')
    
    user = db_ops.get_user_by_username(username)
    return render_template("my_profile.html", user=user)

@app.route('/recipes/create_recipe', methods=['GET', 'POST'])
def create_recipe():
    form = RecipeForm()
    
    if request.method == 'POST':
        ingredient_infos = {}
        for ingredient_form in form.ingredients.entries:
            spoonacular_id = ingredient_form.spoonacular_id.data
            if spoonacular_id:
                ingredient_info = db_ops.get_ingredient_info(spoonacular_id, ingredient_form.quantity.data, ingredient_form.unit.data)
                name, spoonacular_id, image_url, nutrients = db_ops.process_ingredient_info(ingredient_info)
                
                if name and spoonacular_id:
                    ingredient_infos[ingredient_form.spoonacular_id.data] = (name, spoonacular_id, image_url, nutrients)
                    possible_units = ingredient_info.get('possibleUnits', [])
                    ingredient_form.unit.choices = [(unit, unit) for unit in possible_units]
                else:
                    ingredient_form.unit.choices = []

        if form.validate_on_submit():
            new_recipe = db_ops.create_recipe(
                username=session['username'],
                title=form.title.data,
                description=form.description.data,
                instructions=form.instructions.data
            )

            for ingredient_form in form.ingredients.entries:
                name, spoonacular_id, image_url, nutrients = ingredient_infos.get(ingredient_form.spoonacular_id.data, (None, None, None, []))
                if name and spoonacular_id:
                    ingredient_id = db_ops.store_ingredient(name, spoonacular_id, image_url, nutrients)
                    db_ops.create_recipe_ingredient(new_recipe.recipe_id, ingredient_id, ingredient_form.quantity.data, ingredient_form.unit.data)

            db_ops.commit_session()
            flash('Recipe added successfully', 'success')
            return redirect(f"/recipes/{new_recipe.recipe_id}")

    csrf_token = form.csrf_token._value()
    return render_template('create_recipe.html', form=form, SPOONACULAR_API_KEY=db_ops.SPOONACULAR_API_KEY, csrf_token=csrf_token)

@app.route('/get_csrf_token', methods=['GET'])
def get_csrf_token():
    csrf_token = generate_csrf()
    return jsonify(csrf_token=csrf_token)

@app.route("/recipes/<recipe_id>")
def show_recipe(recipe_id):
    recipe = db_ops.get_recipe_by_id(recipe_id)
    overall_nutritional_values = db_ops.calculate_nutritional_values(recipe)
    return render_template('recipe_info.html', recipe=recipe, overall_nutritional_values=overall_nutritional_values)

@app.route('/my_recipes')
def my_recipes():
    recipes = Recipe.query.filter_by(username=session['username']).all()
    return render_template('my_recipes.html', recipes=recipes)
