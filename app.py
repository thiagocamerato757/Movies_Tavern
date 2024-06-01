from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# Sua chave de API do TMDb
API_KEY = 'b1caf5476a4a9ee94eb6aa3741ee91b4'

def get_featured_movies():
    """
    Obtém uma lista de filmes populares da API do TMDb.
    
    Retorna:
        List[Dict]: Uma lista de dicionários contendo títulos e caminhos dos pôsteres dos filmes.
    """
    url = f'https://api.themoviedb.org/3/movie/popular?api_key={API_KEY}'
    response = requests.get(url) # Faz uma requisição GET à API do TMDb
    data = response.json() # Converte a resposta em JSON
    movies = []
    results = data.get('results', [])[:6] # Obtém a lista de resultados
    
    for movie in results:
        movie_data = {
            'title': movie.get('title'), # Título do filme
            'poster_path': movie.get('poster_path') # Caminho do pôster do filme
        }
        movies.append(movie_data) # Adiciona o filme à lista de filmes
    return movies

@app.route('/')
def home():
    """
    Rota principal que renderiza a página inicial com filmes em destaque.
    
    Retorna:
        Template HTML: A página inicial com filmes populares.
    """
    featured_movies = get_featured_movies()
    return render_template('TelaInicial.html',featured_movies=featured_movies)

@app.route('/search', methods=['GET'])
def search():
    """
    Rota de busca que permite ao usuário procurar por filmes específicos.
    
    Parâmetros de URL:
        query (str): O termo de busca inserido pelo usuário.
    
    Retorna:
        Template HTML: A página de resultados da busca com a lista de filmes correspondentes.
    """
    query = request.args.get('query') # Obtém o termo de busca da URL
    if query:
        # Faz uma requisição GET à API do TMDb para buscar filmes
        url = f'https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={query}'
        response = requests.get(url)
        data = response.json() # Converte a resposta em JSON
        movies = data.get('results', []) # Obtém a lista de resultados
    else:
        movies = [] # Se não houver termo de busca, a lista de filmes é vazia
    return render_template('search.html', movies=movies)

@app.route('/movie/<int:movie_id>')
def movie_detail(movie_id):
    """
    Rota de detalhes do filme que exibe informações detalhadas de um filme específico.
    
    Parâmetros de URL:
        movie_id (int): O ID do filme a ser exibido.
    
    Retorna:
        Template HTML: A página de detalhes do filme.
    """
    # Faz uma requisição GET à API do TMDb para obter detalhes do filme
    url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}'
    response = requests.get(url)
    movie = response.json() # Converte a resposta em JSON
    return render_template('movie.html', movie=movie) # Renderiza o template com os detalhes do filme

if __name__ == '__main__':
    app.run(debug=True, port=8001) # Executa o aplicativo Flask no modo debug

