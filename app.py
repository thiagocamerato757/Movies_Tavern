from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# Sua chave de API do TMDb
API_KEY = 'b1caf5476a4a9ee94eb6aa3741ee91b4'

def get_featured_movies():
    url = f'https://api.themoviedb.org/3/movie/popular?api_key={API_KEY}'
    response = requests.get(url)
    data = response.json()
    movies = []
    results = data.get('results', [])
    for movie in results:
        movie_data = {
            'title': movie.get('title'),
            'poster_path': movie.get('poster_path')
        }
        movies.append(movie_data)
    return movies

@app.route('/')
def home():
    featured_movies = get_featured_movies()
    return render_template('TelaInicial.html',featured_movies=featured_movies)

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    if query:
        url = f'https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={query}'
        response = requests.get(url)
        data = response.json()
        movies = data.get('results', [])
    else:
        movies = []
    return render_template('search.html', movies=movies)

@app.route('/movie/<int:movie_id>')
def movie_detail(movie_id):
    url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}'
    response = requests.get(url)
    movie = response.json()
    return render_template('movie.html', movie=movie)

if __name__ == '__main__':
    app.run(debug=True, port=8001)
