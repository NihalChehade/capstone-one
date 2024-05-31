import unittest
from app import app, db, SPOONACULAR_API_KEY
from models import User, Recipe, Ingredient
from forms import SignUpForm
from flask import session
from io import BytesIO
from PIL import Image
from werkzeug.datastructures import FileStorage
class TestAppIntegration(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///test_cook_time'
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

            # Debugging: Print response data
            print("DEBUG: Response data (signup):", response.data.decode('utf-8'))

            self.assertEqual(response.status_code, 302)
            

            user = User.query.filter_by(username='testuser').first()
            self.assertIsNotNone(user)
            self.assertEqual(user.email, 'test@test.com')
            self.assertEqual(user.first_name, 'First')
            self.assertEqual(user.last_name, 'Last')
            self.assertEqual(user.bio, 'Test Bio')

    def test_login(self):
        with app.app_context():
            user = User.signup(
                username='testuser',
                pwd='password',
                email='test@test.com',
                fname='First',
                lname='Last',
                bio='Test Bio',
                image='default_profile.png'
            )
            db.session.add(user)
            db.session.commit()

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
            user = User.signup(
                username='testuser',
                pwd='password',
                email='test@test.com',
                fname='First',
                lname='Last',
                bio='Test Bio',
                image='default_profile.png'
            )
            db.session.add(user)
            db.session.commit()

            self.client.post('/login', data={
                'username': 'testuser',
                'password': 'password'
            }, follow_redirects=True)

            response = self.client.get('/logout', follow_redirects=True)

            # Debugging: Print response data
            print("DEBUG: Response data (logout):", response.data.decode('utf-8'))

            self.assertEqual(response.status_code, 200)
            self.assertIn('You have been logged out', response.data.decode('utf-8'))

    
   