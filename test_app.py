import unittest
from flask_testing import TestCase
from unittest.mock import patch, MagicMock
from app import app, db
import os

class TestApp(TestCase):

    def create_app(self):
        # Configura a aplicação para usar um banco de dados de teste
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///teste.bd'  # Banco de dados de teste
        app.config['WTF_CSRF_ENABLED'] = False
        return app

    def setUp(self):
        # Cria todas as tabelas no banco de dados de teste antes de cada teste
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        # Remove todos os dados do banco de dados de teste após cada teste
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
        if os.path.exists('teste.bd'):
            os.remove('teste.bd')  # Remove o arquivo do banco de dados de teste

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

    def test_cadastro_usuario(self):
        response = self.client.post('/cadastro_usuario', data={
            'username': 'testuser',
            'password': 'testpass'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful registration
        follow_response = self.client.get(response.headers['Location'])
        self.assertIn(b'testuser', follow_response.data)
        self.assertIn(b'Class: Peasant', follow_response.data)

    def test_login(self):
        self.client.post('/cadastro_usuario', data={
            'username': 'testuser',
            'password': 'testpass'
        })
        response = self.client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful login
        follow_response = self.client.get(response.headers['Location'])
        self.assertIn(b'testuser', follow_response.data)
        self.assertIn(b'Class: Peasant', follow_response.data)

    def test_logout(self):
        self.client.post('/cadastro_usuario', data={
            'username': 'testuser',
            'password': 'testpass'
        })
        self.client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass'
        })
        response = self.client.get('/logout')
        self.assertEqual(response.status_code, 302)  # Redirect after successful logout
        follow_response = self.client.get(response.headers['Location'])
        self.assertIn(b'Sign in', follow_response.data)
        self.assertIn(b'Create account', follow_response.data)

    def test_toggle_favorite(self):
        self.client.post('/cadastro_usuario', data={
            'username': 'testuser',
            'password': 'testpass'
        })
        self.client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass'
        })
        
        with self.client.session_transaction() as sess:
            sess['user_id'] = 'testuser'
        
        response = self.client.post('/add_to_favorites', json={
            'movie_id': 1
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Movie added to favorites!', response.data)
        
        response = self.client.post('/toggle_favorite', json={
            'movie_id': 1
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Movie removed from favorites!', response.data)

if __name__ == '__main__':
    unittest.main()