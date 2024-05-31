from flask_migrate import Migrate
from flask import Flask, render_template, redirect, session, flash, request, current_app, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Recipe, Ingredient, NutritionalValue, RecipeIngredient
from forms import SignUpForm, LoginForm, RecipeForm, IngredientForm
import requests
import os
import secrets
from PIL import Image
from flask_wtf.csrf import generate_csrf

from secrett import SPOONACULAR_API_KEY
app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get('DATABASE_URL', 'postgresql://njaicrqz:gyXNe8QlCSAVE4qiBMCTR0tin6LTCYKC@bubble.db.elephantsql.com/njaicrqz')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"
app.config['WTF_CSRF_TIME_LIMIT'] = None  # Disable CSRF expiration for testing, set an appropriate value for production
connect_db(app)

with app.app_context():
 db.create_all()
migrate = Migrate(app, db)
toolbar = DebugToolbarExtension(app)
API_BASE_URL = "https://api.spoonacular.com"
key = SPOONACULAR_API_KEY

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

@app.route('/')
def boarding():
    
    return render_template('index.html')
 

def save_profile_image(form_image):
    print("**************************", form_image)
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
    """sign up a user: produce form & handle form submission."""

    form = SignUpForm()

    if form.validate_on_submit():

        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        bio = form.bio.data
        profile_image = form.profile_image.data

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists please choose a new username!', 'danger')
            return redirect("/signup")
        
        existing_user_by_email = User.query.filter_by(email=email).first()
        if existing_user_by_email:
            flash('Email already in use please choose a new one!', 'danger')
            return redirect("/signup")
        
        # Handle profile image upload
        if form.profile_image.data:
            print("Profile Image Data Type:", type(form.profile_image.data))  # Debug print statement
            profile_image = save_profile_image(form.profile_image.data)
        else:
            profile_image = 'default_profile.png'

        user = User.signup(username, password, email, first_name, last_name, bio=form.bio.data,
            image=profile_image)

        db.session.add(user)
        db.session.commit()

        session["username"] = user.username

        # if logged in, redirect to secret page and flash msg
        flash("Welcome on board!!", "success")
        return redirect("/")

    else:
        return render_template("signup.html", form=form)
    
@app.route("/login", methods=["GET", "POST"])
def login():
    """Generate login form and handle login"""

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
     
        user = User.authenticate(username, password)

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
    """Logs user out, redirects to homepage"""

    session.pop("username")
    flash("You have been logged out", "danger")
    return redirect("/")

@app.route("/users/<username>")
def show_user(username):
    if 'username' not in session:
        flash('You need to be logged in to view your profile.', 'danger')
        return redirect('/login')
    
    user = User.query.filter_by(username=username).first();
    return render_template("my_profile.html", user=user)

@app.route('/recipes/create_recipe', methods=['GET', 'POST'])
def create_recipe():
    form = RecipeForm()

    if request.method == 'POST':
        ingredient_infos = {}
        for ingredient_form in form.ingredients.entries:
            spoonacular_id = ingredient_form.spoonacular_id.data
            if spoonacular_id:
                response = requests.get(f"{API_BASE_URL}/food/ingredients/{spoonacular_id}/information?apiKey={SPOONACULAR_API_KEY}&amount={ingredient_form.quantity.data}&unit={ingredient_form.unit.data}")
                if response.status_code == 200:
                    ingredient_info = response.json()
                    ingredient_infos[spoonacular_id] = ingredient_info
                    possible_units = ingredient_info.get('possibleUnits', [])
                    ingredient_form.unit.choices = [(unit, unit) for unit in possible_units]
                else:
                    ingredient_form.unit.choices = []

        if form.validate_on_submit():
            new_recipe = Recipe(
                username=session['username'],
                title=form.title.data,
                description=form.description.data,
                instructions=form.instructions.data
            )
            db.session.add(new_recipe)
            db.session.flush()  # Ensure the recipe ID is available for ingredients

            for ingredient_form in form.ingredients.entries:
                ingredient_name = ingredient_form.form.name.data
                spoonacular_id = ingredient_form.spoonacular_id.data
                ingredient_info = ingredient_infos.get(spoonacular_id, {})

                existing_ingredient = Ingredient.query.filter_by(name=ingredient_name).first()

                if existing_ingredient:
                    ingredient_id = existing_ingredient.ingredient_id
                else:
                    image_url = ingredient_info.get('image', '')
                    new_ingredient = Ingredient(name=ingredient_name, spoonacular_id=spoonacular_id, image_url=image_url)
                    db.session.add(new_ingredient)
                    db.session.flush()  # Ensure the ingredient ID is available
                    ingredient_id = new_ingredient.ingredient_id

                    if 'nutrition' in ingredient_info:
                        nutrients = ingredient_info['nutrition']['nutrients']
                        for nutrient in nutrients:
                            if nutrient['name'] in SPECIFIED_NUTRIENTS:
                                new_nutritional_value = NutritionalValue(
                                    ingredient_id=new_ingredient.ingredient_id,
                                    nutrient_name=nutrient['name'],
                                    amount=nutrient.get('amount', 0),
                                    unit=nutrient.get('unit', '')
                                )
                                db.session.add(new_nutritional_value)

                recipe_ingredient = RecipeIngredient(
                    recipe_id=new_recipe.recipe_id,
                    ingredient_id=ingredient_id,
                    quantity=ingredient_form.quantity.data,
                    unit=ingredient_form.unit.data
                )
                db.session.add(recipe_ingredient)

            db.session.commit()  # Commit all changes in the transaction after processing all ingredients
            flash('Recipe added successfully', 'success')
            return redirect(f"/recipes/{new_recipe.recipe_id}")
        else:
            print(form.errors)
    csrf_token = form.csrf_token._value()
    return render_template('create_recipe.html', form=form, SPOONACULAR_API_KEY=SPOONACULAR_API_KEY, csrf_token=csrf_token)


@app.route('/get_csrf_token', methods=['GET'])
def get_csrf_token():
    csrf_token = generate_csrf()
    return jsonify(csrf_token=csrf_token)           

@app.route("/recipes/<recipe_id>")
def show_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    overall_nutritional_values = calculate_nutritional_values(recipe)
    return render_template('recipe_info.html', recipe=recipe, overall_nutritional_values=overall_nutritional_values)

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

@app.route('/my_recipes')
def my_recipes():
    recipes = Recipe.query.filter_by(username=session['username']).all()
    print(recipes)
    return render_template('my_recipes.html', recipes=recipes)
    
