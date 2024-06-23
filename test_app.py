import unittest
from flask import Flask
from flask_testing import TestCase
from unittest.mock import patch, MagicMock
import app

class TestApp(TestCase):

    def create_app(self):
        app.app.config['TESTING'] = True
        app.app.config['WTF_CSRF_ENABLED'] = False  # Desabilitar CSRF para testes
        return app.app

    @patch('app.get_featured_movies')
    def test_home(self, mock_get_featured_movies):
        mock_get_featured_movies.return_value = [
            {'title': 'Movie 1', 'poster_path': '/path1.jpg', 'id': 1},
            {'title': 'Movie 2', 'poster_path': '/path2.jpg', 'id': 2},
        ]

        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assert_template_used('TelaInicial.html')
        self.assertIn(b'Movie 1', response.data)
        self.assertIn(b'Movie 2', response.data)

    @patch('app.requests.get')
    def test_search(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'results': [
                {'title': 'Search Movie 1', 'poster_path': '/search_path1.jpg', 'id': 3},
                {'title': 'Search Movie 2', 'poster_path': '/search_path2.jpg', 'id': 4},
            ]
        }
        mock_get.return_value = mock_response

        response = self.client.get('/search?query=test')
        self.assertEqual(response.status_code, 200)
        self.assert_template_used('search.html')
        self.assertIn(b'Search Movie 1', response.data)
        self.assertIn(b'Search Movie 2', response.data)

    @patch('app.requests.get')
    def test_movie_detail(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'title': 'Detailed Movie', 'poster_path': '/detail_path.jpg', 'id': 5,
            'overview': 'This is a detailed movie description.'
        }
        mock_get.return_value = mock_response

        response = self.client.get('/movie/5')
        self.assertEqual(response.status_code, 200)
        self.assert_template_used('movie.html')
        self.assertIn(b'Detailed Movie', response.data)
        self.assertIn(b'This is a detailed movie description.', response.data)

    @patch('app.bcrypt.generate_password_hash')
    @patch('app.Session')
    def test_cadastro_usuario(self, mock_session, mock_generate_password_hash):
        mock_generate_password_hash.return_value = b'hashed_password'
        mock_session_instance = mock_session.return_value
        mock_session_instance.add.return_value = None
        mock_session_instance.commit.return_value = None

        response = self.client.post('/cadastro_usuario', data={
            'username': 'testuser',
            'password': 'testpassword'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn('User registered successfully!', response.get_data(as_text=True))

    @patch('app.Session')
    def test_login_success(self, mock_session):
        mock_session_instance = mock_session.return_value
        mock_user = MagicMock()
        mock_user.UserName = 'testuser'
        mock_user.Passworld = b'$2b$12$KIXi5TQGJb4.lhIx/h2xie2fGcxpKuExRx3ZT3vKmD6eLR6ZChz.e'  # bcrypt hash para 'testpassword'
        mock_user.Class = 'campones'
        mock_session_instance.query.return_value.filter_by.return_value.first.return_value = mock_user

        with patch('app.bcrypt.check_password_hash') as mock_check_password_hash:
            mock_check_password_hash.return_value = True

            response = self.client.post('/login', data={
                'username': 'testuser',
                'password': 'testpassword'
            }, follow_redirects=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn('Logged in successfully!', response.get_data(as_text=True))

    @patch('app.Session')
    def test_login_failure(self, mock_session):
        mock_session_instance = mock_session.return_value
        mock_session_instance.query.return_value.filter_by.return_value.first.return_value = None

        response = self.client.post('/login', data={
            'username': 'wronguser',
            'password': 'wrongpassword'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn('Invalid username or password', response.get_data(as_text=True))

if __name__ == '__main__':
    unittest.main()
