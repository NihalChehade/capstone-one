from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, TextAreaField, FileField,  SelectField, FieldList, FormField, HiddenField, DecimalField, SubmitField
from wtforms.validators import InputRequired, DataRequired, Email, Length, NumberRange
from flask_wtf.file import FileAllowed

class SignUpForm(FlaskForm):
    """Form for sign up a user."""

    username = StringField("Username", validators=[DataRequired(), Length(min=4, max=25)])
    password = PasswordField("Password", validators=[DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long')])
    email = EmailField('Email address', validators=[DataRequired(), Email()])
    first_name = StringField("First Name", validators = [DataRequired(), Length(min=1, max=30)])
    last_name = StringField("Last Name", validators=[InputRequired(), Length(min=1, max=30)])
    bio = TextAreaField('Bio', validators=[Length(max=500)])
    profile_image = FileField('Profile Image', validators=[FileAllowed(['jpg', 'png'], 'Images only!')])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    """Form for registering a user."""

    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])


class IngredientForm(FlaskForm):
    name = StringField('Type the first three letters of Ingredient Name and then select an option', validators=[DataRequired()])
    quantity = DecimalField('Quantity', validators=[DataRequired(), NumberRange(min=0.01, message='Quantity must be positive')])
    unit = SelectField('Unit', choices=[], validators=[DataRequired()])
    spoonacular_id = HiddenField()

class RecipeForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=4, max=25)])
    description = TextAreaField('Description', validators=[DataRequired()])
    instructions = TextAreaField('Instructions', validators=[DataRequired()], render_kw={"rows": 10, "cols": 30})
    ingredients = FieldList(FormField(IngredientForm), min_entries=1)
    submit = SubmitField('Create Recipe')