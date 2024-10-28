import unittest
from unittest.mock import patch
from flask import Flask
from apps.authentication.models import Users, user_loader, request_loader

class TestUserAuthentication(unittest.TestCase):

    def setUp(self):
        # Create a Flask app for testing purposes
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True

        # Set up a test client and establish the application context
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()

        # Set up a test user
        self.test_user = Users(id=1, username='testuser', email='test@example.com', password='password123')

    def tearDown(self):
        # Clean up: pop the application context after each test
        self.ctx.pop()

    def test_user_loader(self):
        # Mocking the Users.query.filter_by(id=id).first() call
        with patch('apps.authentication.models.Users.query') as mock_query:
            mock_query.filter_by.return_value.first.return_value = self.test_user
            loaded_user = user_loader(1)
            self.assertEqual(loaded_user, self.test_user)

    def test_request_loader(self):
        # Mocking the Users.query.filter_by(username=username).first() call
        with patch('apps.authentication.models.Users.query') as mock_query:
            mock_query.filter_by.return_value.first.return_value = self.test_user
            request_mock = unittest.mock.Mock()
            request_mock.form.get.return_value = 'testuser'
            loaded_user = request_loader(request_mock)
            self.assertEqual(loaded_user, self.test_user)

if __name__ == '__main__':
    unittest.main()
