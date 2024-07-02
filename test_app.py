import unittest
from flask_testing import TestCase
from unittest.mock import patch, MagicMock
from app import app, db
from entidades import User_Class
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
        # Testa a rota principal que exibe a tela inicial com filmes populares
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
        # Testa a rota de busca de filmes
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
    def test_cadastro_usuario(self):
        # Testa o cadastro de um novo usuário
        response = self.client.post('/cadastro_usuario', data={
            'username': 'testuser',
            'password': 'testpass'
        })
        self.assertEqual(response.status_code, 302)  # Redirect após cadastro bem-sucedido
        follow_response = self.client.get(response.headers['Location'])
        self.assertIn(b'testuser', follow_response.data)
        self.assertIn(b'Class: Peasant', follow_response.data)

    @patch('app.requests.get')
    def test_movie_detail(self, mock_get):
        mock_movie_response = {
            'title': 'Example Movie',
            'genres': [{'name': 'Action'}, {'name': 'Comedy'}],
            'id': 5,
            'poster_path': '/path/to/poster.jpg'  # Adicionando 'poster_path' no mock response
        }
        mock_credits_response = {
            'cast': [{'name': 'Actor 1'}, {'name': 'Actor 2'}]
        }
        mock_get.side_effect = [
            unittest.mock.Mock(status_code=200, json=lambda: mock_movie_response),
            unittest.mock.Mock(status_code=200, json=lambda: mock_credits_response)
        ]

        response = self.client.get('/movie/5')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Example Movie', response.data)
        self.assertIn(b'Action', response.data)
        self.assertIn(b'Comedy', response.data)

    @patch('app.flask_session', {'user_id': 'test_user'})
    @patch('app.Session')
    def test_toggle_favorite(self, mock_session):
        mock_session_instance = mock_session.return_value
        mock_query = mock_session_instance.query.return_value
        mock_query.filter_by.return_value.first.return_value = None

        response = self.client.post('/add_to_favorites', json={'movie_id': 5})
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertIsNotNone(json_data)
        self.assertEqual(json_data['status'], 'added')

    def test_logout(self):
        # Testa o logout de um usuário
        self.client.post('/cadastro_usuario', data={
            'username': 'testuser',
            'password': 'testpass'
        })
        self.client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass'
        })
        response = self.client.get('/logout')
        self.assertEqual(response.status_code, 302)  # Redirect após logout bem-sucedido
        follow_response = self.client.get(response.headers['Location'])
        self.assertIn(b'Sign in', follow_response.data)
        self.assertIn(b'Create account', follow_response.data)
        
    def test_calculate_user_class_paladino(self):
        favorite_movies = [
            {'genres': [{'id': 10751, 'name': 'Family'}, {'id': 12, 'name': 'Adventure'}]},  # Paladino
            {'genres': [{'id': 10751, 'name': 'Family'}, {'id': 14, 'name': 'Fantasy'}]},    # Paladino, Mago
            {'genres': [{'id': 10751, 'name': 'Family'}, {'id': 18, 'name': 'Drama'}]},      # Paladino, Clérigo
            {'genres': [{'id': 12, 'name': 'Adventure'}, {'id': 99, 'name': 'Documentary'}]} # Paladino, Clérigo
        ]

        user_class = User_Class()
        user_class.calculate_user_class(favorite_movies)
        self.assertEqual(user_class.class_user, "Paladino")

    def test_calculate_user_class_mago(self):
        favorite_movies = [
            {'genres': [{'id': 14, 'name': 'Fantasy'}, {'id': 878, 'name': 'Science Fiction'}]},  # Mago
            {'genres': [{'id': 878, 'name': 'Science Fiction'}, {'id': 16, 'name': 'Animation'}]}, # Mago, Druida
            {'genres': [{'id': 878, 'name': 'Science Fiction'}, {'id': 28, 'name': 'Action'}]},    # Mago, Guerreiro
            {'genres': [{'id': 14, 'name': 'Fantasy'}, {'id': 99, 'name': 'Documentary'}]},        # Mago, Clérigo
            {'genres': [{'id': 878, 'name': 'Science Fiction'}, {'id': 10751, 'name': 'Family'}]}  # Mago, Paladino
        ]

        user_class = User_Class()
        user_class.calculate_user_class(favorite_movies)
        self.assertEqual(user_class.class_user, "Mago")

    def test_calculate_user_class_guerreiro(self):
        favorite_movies = [
            {'genres': [{'id': 28, 'name': 'Action'}, {'id': 12, 'name': 'Adventure'}]},           # Guerreiro, Bárbaro
            {'genres': [{'id': 28, 'name': 'Action'}, {'id': 99, 'name': 'Documentary'}]},         # Guerreiro, Clérigo
            {'genres': [{'id': 28, 'name': 'Action'}, {'id': 878, 'name': 'Science Fiction'}]},    # Guerreiro, Mago
            {'genres': [{'id': 28, 'name': 'Action'}, {'id': 10751, 'name': 'Family'}]}            # Guerreiro, Paladino
        ]

        user_class = User_Class()
        user_class.calculate_user_class(favorite_movies)
        self.assertEqual(user_class.class_user, "Guerreiro")


if __name__ == '__main__':
    unittest.main()
