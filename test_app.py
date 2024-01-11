import unittest
from app import app, db, User, Comment, Projects, AdminReply

class ProjectsTestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = app.test_client()
        self.runner = app.test_cli_runner()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def login(self, username, password):
        return self.client.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def test_index_page(self):
        with app.app_context():
            db.create_all()
            # Create a user
            user = User(username='TestUsername', name="Test User")
            user.set_password('TestPassword')
            db.session.add(user)
            db.session.commit()

            # Login with the created user
            self.login('TestUsername', 'TestPassword')

            # Test index page
            response = self.client.get('/')
            data = response.get_data(as_text=True)
            expected_title = f"{user.name}'s Blog"
            self.assertIn(expected_title, data)
            self.assertIn('0 Titles', data)
            self.assertEqual(response.status_code, 200)

    def test_login_logout(self):
        with app.app_context():
            db.create_all()
            user = User.query.filter_by(username='TestUsername').first()
            if user is None:
                user = User(username='TestUsername', name='Test User')
                user.set_password('TestPassword')
                db.session.add(user)
                db.session.commit()

            # Test login
            response = self.login('TestUsername', 'TestPassword')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Login success.', response.data)

            # Test logout
            response = self.client.get('/logout', follow_redirects=True)
            self.assertIn(b'Goodbye.', response.data)

    def test_create_item(self):
        with app.app_context():
            db.create_all()
            # Create user
            user = User(username='TestUsername', name='Test User')
            user.set_password('TestPassword')
            db.session.add(user)
            db.session.commit()

            # Login with the created user
            response = self.login('TestUsername', 'TestPassword')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Login success.', response.data)

            # Test create item
            response = self.client.post('/', data=dict(
                title='New Title'
            ), follow_redirects=True)
            self.assertIn(b'Add successfully', response.data)
            self.assertIn(b'New Title', response.data)

    # comment还没写...

if __name__ == '__main__':
    unittest.main()

