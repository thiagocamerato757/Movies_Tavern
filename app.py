from flask import Flask, render_template, request
import requests
import re

app = Flask(__name__)

if not app.config.get('TESTING', False):
    file = ".config"
    contents = open(file, "r").read()
    config = eval(contents)
    API_KEY = config['API_KEY']
else:
    API_KEY = "test_api_key"  # Use uma chave de API de teste durante os testes

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
            'poster_path': movie.get('poster_path'), # Caminho do pôster do filme
            'id': movie.get('id')
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
    page = request.args.get('page', 1, type=int) 
    if query:
        # Faz uma requisição GET à API do TMDb para buscar filmes
        url = f'https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={query}&page={page}&sort_by=vote_average.desc'
        response = requests.get(url)
        data = response.json() # Converte a resposta em JSON
        movies = data.get('results', []) # Obtém a lista de resultados
        sorted_movies = sorted(movies, key=lambda x: x['title']) #ordenando filmes pelo título
        total_pages = data.get('total_pages', 1)
    else:
        movies = [] # Se não houver termo de busca, a lista de filmes é vazia
        total_pages = 1
    return render_template('search.html', movies=sorted_movies,query=query, page=page, total_pages=total_pages)

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

def pagination_range(current_page, total_pages, delta=1):
    """
    Generate pagination range for displaying limited pages with '...' in between.
    
    :param current_page: The current active page.
    :param total_pages: The total number of pages.
    :param delta: The number of pages to display around the current page.
    :return: A list with the pagination range and '...' as None.
    """
    range_with_dots = []
    for p in range(1, total_pages + 1):
        if p == 1 or p == total_pages or (current_page - delta <= p <= current_page + delta):
            range_with_dots.append(p)
        elif range_with_dots[-1] is not None:
            range_with_dots.append(None)
    return range_with_dots

@app.context_processor
def utility_processor():
    return dict(pagination_range=pagination_range)

if __name__ == '__main__':
    app.run(debug=True, port=8001) # Executa o aplicativo Flask no modo debug

