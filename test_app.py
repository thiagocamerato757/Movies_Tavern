import unittest
from flask import Flask
from flask_testing import TestCase
from unittest.mock import patch, MagicMock
import app  

class TestApp(TestCase):

    def create_app(self):
        app.app.config['TESTING'] = True
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

if __name__ == '__main__':
    unittest.main()
