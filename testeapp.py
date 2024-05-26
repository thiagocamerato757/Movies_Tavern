from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# Sua chave de API do TMDb
API_KEY = 'b1caf5476a4a9ee94eb6aa3741ee91b4'

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    movies = []
    if query:
        url = f'https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={query}'
        response = requests.get(url)
        data = response.json()
        results = data.get('results', [])
        for movie in results:
            movie_data = {
                'title': movie.get('title'),
                'poster_path': movie.get('poster_path')
            }
            movies.append(movie_data)
    return render_template('index.html', movies=movies)

if __name__ == '__main__':
    app.run(debug=True)