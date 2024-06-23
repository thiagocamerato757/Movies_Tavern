from flask_bcrypt import Bcrypt
from flask import Flask, render_template, request, redirect, url_for,flash,session as flask_session, jsonify
import requests
import re
from sqlalchemy.exc import IntegrityError  # Corrigido: import correto do IntegrityError
from entidades import *

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Gera uma chave secreta aleatória para desenvolvimento
bcrypt = Bcrypt(app)  # Inicializa o Bcrypt para hashing de senha
global usuario
usuario = None
global classe
classe = None

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
    return render_template('TelaInicial.html', featured_movies=featured_movies)


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
    return render_template('search.html', movies=sorted_movies, query=query, page=page, total_pages=total_pages)

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
    movie_url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}'
    movie_response = requests.get(movie_url)
    movie = movie_response.json() # Converte a resposta em JSON
    
    # Faz uma requisição GET à API do TMDb para obter o elenco do filme
    credits_url = f'https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={API_KEY}'
    credits_response = requests.get(credits_url)
    credits = credits_response.json()
    cast = credits.get('cast', [])

    is_favorite = False
    if 'user_id' in flask_session:
        user_id = flask_session['user_id']
        session_db = Session()
        favorite = session_db.query(ListaFavoritos).filter_by(userName=user_id, movie_id=movie_id).first()
        is_favorite = favorite is not None
        session_db.close()
    
    return render_template('movie.html', movie=movie, cast=cast, movie_id=movie_id,is_favorite=is_favorite) # Renderiza o template com os detalhes do filme e do elenco

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

# Processador de contexto para disponibilizar a função de paginação nos templates
@app.context_processor
def utility_processor():
    return dict(pagination_range=pagination_range)

# Rota para o formulário de cadastro de usuário
@app.route('/form')
def form():
    return render_template("cadastro.html")

# Rota para o cadastro de usuário
@app.route('/cadastro_usuario', methods=['POST'])
def cadastro_usuario():
    session_db = Session()
    username = request.form.get("username")
    password = request.form.get("password")
    user_class = "Peasant"

    if username and password:
        password_hash = bcrypt.generate_password_hash(password).decode("utf-8")
        user = User(UserName=username, Passworld=password_hash, Class=user_class)

        try:
            session_db.add(user)
            session_db.commit()
            flash('User registered successfully!', 'success')
            flask_session['user_id'] = username
            flask_session['user_class'] = user_class
            return redirect(url_for('perfil'))
        except IntegrityError:
            session_db.rollback()
            flash("Error: Username already registered", "error")
            return redirect(url_for('form'))
        finally:
            session_db.close()
    else:
        flash("Invalid Data", "error")
        return redirect(url_for('form'))

# Rota para o processo de login
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username and password:
            session_db = Session()
            user = session_db.query(User).filter_by(UserName=username).first()

            if user and bcrypt.check_password_hash(user.Passworld, password):
                flask_session['user_id'] = user.UserName
                flask_session['user_class'] = user.Class
                flash('Logged in successfully!', 'success')
                return redirect(url_for('perfil'))
            else:
                flash("Invalid username or password", "error")
            session_db.close()
        else:
            flash("Username and password are required", "error")

    return render_template('login.html')

# Rota para o logout do usuário
@app.route('/logout')
def logout():
    flask_session.pop('user_id', None)
    flask_session.pop('user_class', None)
    return redirect(url_for('home'))


# Rota para a página de perfil do usuário
@app.route('/perfil')
def perfil():
    if 'user_id' in flask_session:
        user_id = flask_session['user_id']
        session_db = Session()
        
        try:
            # Buscando os filmes favoritos do usuário
            favoritos = session_db.query(ListaFavoritos).filter_by(userName=user_id).all()
            filmes_favoritos = []
            for favorito in favoritos:
                # Fazendo uma requisição para a API TMDb para obter detalhes do filme
                movie_id = favorito.movie_id
                movie_url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}'
                movie_response = requests.get(movie_url)
                if movie_response.status_code == 200:
                    movie = movie_response.json()
                    filmes_favoritos.append(movie)
        except:
            flash('Error loading favorite movies', 'error')
            return redirect(url_for('login'))
        finally:
            session_db.close()

        return render_template('perfil.html', usuario=flask_session['user_id'], classe=flask_session['user_class'], favorito=filmes_favoritos)
    else:
        flash('You need to log in first', 'error')
        return redirect(url_for('login'))
    

# Rota para adicionar/remover um filme da lista de favoritos
@app.route('/toggle_favorite', methods=['POST'])
def toggle_favorite():
    if 'user_id' not in flask_session:
        return jsonify({'error': 'You must be logged in to favorite a movie.'}), 401

    data = request.get_json()
    movie_id = data.get('movie_id')
    user_id = flask_session['user_id']

    session_db = Session()
    try:
        favorite = session_db.query(ListaFavoritos).filter_by(userName=user_id, movie_id=movie_id).first()
        if favorite:
            session_db.delete(favorite)
            session_db.commit()
            return jsonify({'message': 'Movie removed from favorites!'})
        else:
            new_favorite = ListaFavoritos(userName=user_id, movie_id=movie_id)
            session_db.add(new_favorite)
            session_db.commit()
            return jsonify({'message': 'Movie added to favorites!'})
    except IntegrityError:
        session_db.rollback()
        return jsonify({'error': 'An error occurred.'}), 400
    finally:
        session_db.close()

if __name__ == '__main__':
    app.run(debug=True, port=8001) # Executa o aplicativo Flask no modo debug
