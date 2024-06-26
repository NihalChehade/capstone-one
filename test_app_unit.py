import unittest
from app import app, save_profile_image
from forms import SignUpForm, LoginForm, RecipeForm, IngredientForm
from models import db, Recipe, Ingredient, NutritionalValue, User, RecipeIngredient
from io import BytesIO
from PIL import Image
import os
from werkzeug.datastructures import FileStorage
import db_operations as db_ops

class TestAppUnit(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('TEST_DATABASE_URL','postgresql:///test_cook_time')
        self.client = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_save_profile_image(self):
        with app.app_context():
            image = Image.new('RGB', (100, 100), color='red')
            image_file = BytesIO()
            image.save(image_file, format='JPEG')
            image_file.seek(0)
            
            form_image = FileStorage(stream=image_file, filename='test_image.jpg', content_type='image/jpeg')
            
            picture_fn = save_profile_image(form_image)
            picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
            
            self.assertTrue(os.path.exists(picture_path))

            os.remove(picture_path)

    def test_calculate_nutritional_values(self):
        with app.app_context():
            recipe = Recipe(title='Test Recipe', description='Test Description', instructions='Test Instructions')
            db.session.add(recipe)
            db.session.commit()

            ingredient = Ingredient(name='Test Ingredient', spoonacular_id='12345')
            db.session.add(ingredient)
            db.session.commit()

            nutritional_value = NutritionalValue(nutrient_name='Calories', amount=100, unit='kcal', ingredient_id=ingredient.ingredient_id)
            db.session.add(nutritional_value)
            db.session.commit()
            
            ingredient.nutritional_values.append(nutritional_value)
            recipe_ingredient = RecipeIngredient(recipe_id=recipe.recipe_id, ingredient_id=ingredient.ingredient_id, quantity=1, unit='pcs')
            db.session.add(recipe_ingredient)
            db.session.commit()
            
            recipe.recipes_ingredients_assoc.append(recipe_ingredient)
            db.session.commit()
            
            result = db_ops.calculate_nutritional_values(recipe)
            
            self.assertIn('Calories', result)
            self.assertEqual(result['Calories'], 100)
            self.assertIn('units', result)
            self.assertEqual(result['units']['Calories'], 'kcal')

    def test_user_signup(self):
        with app.app_context():
            image = Image.new('RGB', (100, 100), color='red')
            image_file = BytesIO()
            image.save(image_file, format='JPEG')
            image_file.seek(0)
            
            form_image = FileStorage(stream=image_file, filename='test_image.jpg', content_type='image/jpeg')
            
            response = self.client.post('/signup', data={
                'username': 'testuser',
                'password': 'password',
                'confirm_password': 'password',
                'email': 'test@test.com',
                'first_name': 'First',
                'last_name': 'Last',
                'bio': 'Test Bio',
                'profile_image': form_image
            }, content_type='multipart/form-data', follow_redirects=True)

            self.assertEqual(response.status_code, 200)

            user = db_ops.get_user_by_username('testuser')

            self.assertIsNotNone(user)
            self.assertEqual(user.email, 'test@test.com')
            self.assertEqual(user.first_name, 'First')
            self.assertEqual(user.last_name, 'Last')
            self.assertEqual(user.bio, 'Test Bio')

    def test_user_login(self):
        with app.app_context():
            user = db_ops.create_user('testuser', 'password', 'test@test.com', 'First', 'Last', 'Test Bio', 'default_profile.png')
            db.session.add(user)
            db.session.commit()

            response = self.client.post('/login', data={
                'username': 'testuser',
                'password': 'password'
            }, follow_redirects=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn('Login successful', response.data.decode('utf-8'))

if __name__ == '__main__':
    unittest.main()
