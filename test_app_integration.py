import unittest
import os
from app import app, db
from models import User, Recipe, Ingredient, RecipeIngredient, NutritionalValue
from io import BytesIO
from PIL import Image
from werkzeug.datastructures import FileStorage
import db_operations as db_ops

class TestAppIntegration(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('TEST_DATABASE_URL','postgresql:///test_cook_time')
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_signup(self):
        with app.app_context():
            # Create a valid image file in memory
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
            }, content_type='multipart/form-data', follow_redirects=False)

            

            self.assertEqual(response.status_code, 302)

            user = db_ops.get_user_by_username('testuser')
            self.assertIsNotNone(user)
            self.assertEqual(user.email, 'test@test.com')
            self.assertEqual(user.first_name, 'First')
            self.assertEqual(user.last_name, 'Last')
            self.assertEqual(user.bio, 'Test Bio')

    def test_login(self):
        with app.app_context():
            user = db_ops.create_user(
                username='testuser',
                password='password',
                email='test@test.com',
                first_name='First',
                last_name='Last',
                bio='Test Bio',
                profile_image='default_profile.png'
            )

            with self.client as client:
                response = client.post('/login', data={
                    'username': 'testuser',
                    'password': 'password'
                }, follow_redirects=True)

                # Debugging: Print response data
                print("DEBUG: Response data (login):", response.data.decode('utf-8'))

                self.assertEqual(response.status_code, 200)
                self.assertIn('Login successful', response.data.decode('utf-8'))

                # Check the session
                with client.session_transaction() as session:
                    self.assertEqual(session['username'], 'testuser')

    def test_logout(self):
        with app.app_context():
            user = db_ops.create_user(
                username='testuser',
                password='password',
                email='test@test.com',
                first_name='First',
                last_name='Last',
                bio='Test Bio',
                profile_image='default_profile.png'
            )

            self.client.post('/login', data={
                'username': 'testuser',
                'password': 'password'
            }, follow_redirects=True)

            response = self.client.get('/logout', follow_redirects=True)

            # Debugging: Print response data
            print("DEBUG: Response data (logout):", response.data.decode('utf-8'))

            self.assertEqual(response.status_code, 200)
            self.assertIn('You have been logged out', response.data.decode('utf-8'))

    def test_show_user_profile(self):
        with app.app_context():
            user = db_ops.create_user(
                username='testuser',
                password='password',
                email='test@test.com',
                first_name='First',
                last_name='Last',
                bio='Test Bio',
                profile_image='default_profile.png'
            )

            self.client.post('/login', data={
                'username': 'testuser',
                'password': 'password'
            }, follow_redirects=True)

            response = self.client.get(f'/users/{user.username}', follow_redirects=True)

            # Debugging: Print response data
            print("DEBUG: Response data (show_user_profile):", response.data.decode('utf-8'))

            self.assertEqual(response.status_code, 200)
            self.assertIn('testuser', response.data.decode('utf-8'))
            self.assertIn('Test Bio', response.data.decode('utf-8'))

    def test_show_recipe(self):
        with app.app_context():
            user = db_ops.create_user(
                username='testuser',
                password='password',
                email='test@test.com',
                first_name='First',
                last_name='Last',
                bio='Test Bio',
                profile_image='default_profile.png'
            )

            self.client.post('/login', data={
                'username': 'testuser',
                'password': 'password'
            }, follow_redirects=True)

            recipe = db_ops.create_recipe(
                username='testuser',
                title='Test Recipe',
                description='Test Description',
                instructions='Test Instructions'
            )

            ingredient_id = db_ops.store_ingredient(
                name='Test Ingredient',
                spoonacular_id=12345,
                image_url='test_image_url',
                nutrients=[{'name': 'Calories', 'amount': 100, 'unit': 'kcal'}]
            )

            db_ops.create_recipe_ingredient(
                recipe_id=recipe.recipe_id,
                ingredient_id=ingredient_id,
                quantity=1,
                unit='pcs'
            )

            db_ops.commit_session()

            response = self.client.get(f'/recipes/{recipe.recipe_id}', follow_redirects=True)

            # Debugging: Print response data
            print("DEBUG: Response data (show_recipe):", response.data.decode('utf-8'))

            self.assertEqual(response.status_code, 200)
            self.assertIn('Test Recipe', response.data.decode('utf-8'))
            self.assertIn('Test Description', response.data.decode('utf-8'))
            self.assertIn('Test Instructions', response.data.decode('utf-8'))
            self.assertIn('Test Ingredient', response.data.decode('utf-8'))

if __name__ == '__main__':
    unittest.main()
