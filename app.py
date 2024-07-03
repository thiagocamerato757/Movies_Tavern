import os
from flask_bcrypt import Bcrypt
from flask import Flask, render_template, request, redirect, url_for, flash, session as flask_session, jsonify
from flask_sqlalchemy import SQLAlchemy
import requests
from sqlalchemy.exc import IntegrityError
from sqlalchemy import desc
from flask_socketio import SocketIO, send
from entidades import *

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dataBase.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)

if not app.config.get('TESTING', False):
    FILE = ".config"
    contents = open(FILE, "r").read()
    config = eval(contents)
    API_KEY = config['API_KEY']
else:
    API_KEY = "test_api_key"

def get_featured_movies():
    """
    Obtém uma lista de filmes populares da API do TMDb.

    Retorna:
        List[Dict]: Uma lista de dicionários contendo títulos e caminhos dos pôsteres dos filmes.
    """
    url = f'https://api.themoviedb.org/3/movie/popular?api_key={API_KEY}'
    response = requests.get(url)
    data = response.json()
    movies = []
    results = data.get('results', [])[:6]
    
    for movie in results:
        movie_data = {
            'title': movie.get('title'),
            'poster_path': movie.get('poster_path'),
            'id': movie.get('id')
        }
        movies.append(movie_data)
    return movies

@app.route('/')
def home():
    """
    Rota principal que exibe a tela inicial com filmes populares.
    """
    user_class = flask_session.get('user_class', None)
    featured_movies = get_featured_movies()
    return render_template('TelaInicial.html', featured_movies=featured_movies, classe=user_class)

@app.route('/search', methods=['GET'])
def search():
    """
    Rota de busca que pesquisa filmes na API do TMDb e exibe os resultados.

    Parâmetros de URL:
        query (str): A consulta de busca.
        page (int): O número da página dos resultados da busca.

    Retorna:
        Template: O template search.html com os resultados da busca.
    """
    query = request.args.get('query')
    page = request.args.get('page', 1, type=int)
    if query:
        url = f'https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={query}&page={page}&sort_by=vote_average.desc'
        response = requests.get(url)
        data = response.json()
        movies = data.get('results', [])
        sorted_movies = sorted(movies, key=lambda x: x['title'])
        total_pages = data.get('total_pages', 1)
    else:
        movies = []
        total_pages = 1
    user_class = flask_session.get('user_class', None)
    return render_template('search.html', movies=sorted_movies, query=query, page=page, total_pages=total_pages, classe=user_class)

@app.route('/movie/<int:movie_id>')
def movie_detail(movie_id):
    """
    Rota que exibe os detalhes de um filme específico, incluindo gêneros e elenco.

    Parâmetros de URL:
        movie_id (int): O ID do filme.

    Retorna:
        Template: O template movie.html com os detalhes do filme.
    """
    movie_url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}'
    movie_response = requests.get(movie_url)
    movie = movie_response.json()
    genres = movie.get('genres')
    genre_names = []
    for genre in genres:
        genre_names.append(genre['name'])

    credits_url = f'https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={API_KEY}'
    credits_response = requests.get(credits_url)
    credits = credits_response.json()
    cast = credits.get('cast', [])
    
    session_db = Session()
    is_favorite = False
    user_rating = None

    if 'user_id' in flask_session:
        user_id = flask_session['user_id']
        favorite = session_db.query(ListaFavoritos).filter_by(userName=user_id, movie_id=movie_id).first()
        is_favorite = favorite is not None
        user_rating_entry = session_db.query(Avaliacao).filter_by(id_filme=movie_id, UserName=user_id).first()
        if user_rating_entry:
            user_rating = user_rating_entry.stars
        comments = get_comments_for_movie(movie_id, user_id)
    else:
        comments = get_comments_for_movie(movie_id, None)
    
    total = 0
    sum_ratings = 0
    for avaliacao in session_db.query(Avaliacao).filter_by(id_filme=movie_id):
        total += 1
        sum_ratings += avaliacao.stars
    average_rating = sum_ratings / total if total > 0 else 0
    average_rating_rounded = round(average_rating, 1)

    session_db.close()
    movie_object = Movie(movie, cast, comments, average_rating_rounded, genre_names)
    user_class = flask_session.get('user_class', None)
    return render_template('movie.html', movie=movie_object, is_favorite=is_favorite, user_rating=user_rating, classe=user_class)

def get_comments_for_movie(movie_id, user_id):
    """
    Obtém os comentários de um filme específico, incluindo os do usuário logado, se houver.

    Parâmetros:
        movie_id (int): O ID do filme.
        user_id (str): O nome de usuário do usuário logado (pode ser None).

    Retorna:
        List[Avaliacao]: Uma lista de objetos Avaliacao contendo os comentários.
    """
    session_db = Session()
    comments = []
    if user_id:
        user_comment = session_db.query(Avaliacao).filter_by(id_filme=movie_id, UserName=user_id).first()
        if user_comment:
            comments.append(user_comment)
        other_comments = session_db.query(Avaliacao).filter(Avaliacao.id_filme == movie_id, Avaliacao.UserName != user_id).order_by(desc(Avaliacao.comentario)).all()
        comments.extend(other_comments)
    else:
        comments = session_db.query(Avaliacao).filter_by(id_filme=movie_id).order_by(desc(Avaliacao.comentario)).all()
    session_db.close()
    return comments

def pagination_range(current_page, total_pages, delta=1):
    """
    Gera uma lista de páginas para paginação com intervalos e elipses.

    Parâmetros:
        current_page (int): A página atual.
        total_pages (int): O total de páginas.
        delta (int): O intervalo de páginas ao redor da página atual.

    Retorna:
        List[Union[int, None]]: Uma lista de números de páginas e elipses (None).
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
    """
    Processador de contexto para adicionar a função pagination_range ao contexto do template.
    """
    return dict(pagination_range=pagination_range)

@app.route('/form')
def form():
    """
    Rota que exibe o formulário de cadastro de usuário.
    """
    return render_template("cadastro.html")

@app.route('/cadastro_usuario', methods=['POST'])
def cadastro_usuario():
    """
    Rota que realiza o cadastro de um novo usuário.

    Retorna:
        Redirect: Redireciona para a página de perfil se o cadastro for bem-sucedido, 
        ou para o formulário de cadastro se ocorrer um erro.
    """
    session_db = Session()
    username = request.form.get("username")
    password = request.form.get("password")
    user_class = User_Class()

    if username and password:
        password_hash = bcrypt.generate_password_hash(password)
        user = Usuario(username, password_hash, user_class)
        user_db = User(UserName=user.name, Password=user.password, Class=user.user_class.class_user)

        try:
            session_db.add(user_db)
            session_db.commit()
            flash('User registered successfully!', 'success')
            flask_session['user_id'] = username
            flask_session['user_class'] = user.user_class.class_user
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

@app.route('/login', methods=['POST', 'GET'])
def login():
    """
    Rota que realiza o login do usuário.

    Métodos:
        POST: Realiza a autenticação do usuário.
        GET: Exibe o formulário de login.

    Retorna:
        Redirect: Redireciona para a página de perfil se o login for bem-sucedido,
        ou recarrega a página de login se ocorrer um erro.
    """
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username and password:
            session_db = Session()
            user_db = session_db.query(User).filter_by(UserName=username).first()
            session_db.close()

            if user_db and bcrypt.check_password_hash(user_db.Password, password):
                user = Usuario(user_db.UserName, user_db.Password, User_Class(user_db.Class))
                flask_session['user_id'] = user.name
                flask_session['user_class'] = user.user_class.class_user
                
                # Load user's favorite movies
                session_db = Session()
                favorites = session_db.query(ListaFavoritos).filter_by(userName=user.name).all()
                favorite_movies = []
                for favorite in favorites:
                    movie_url = f'https://api.themoviedb.org/3/movie/{favorite.movie_id}?api_key={API_KEY}'
                    movie_response = requests.get(movie_url)
                    if movie_response.status_code == 200:
                        movie = movie_response.json()
                        favorite_movies.append(movie)
                session_db.close()
                flask_session['favorite_movies'] = favorite_movies

                flash('Logged in successfully!', 'success')
                return redirect(url_for('perfil'))
            else:
                flash("Invalid username or password", "error")
        else:
            flash("Username and password are required", "error")

    return render_template('login.html')

@app.route('/logout')
def logout():
    """
    Rota que realiza o logout do usuário.

    Retorna:
        Redirect: Redireciona para a página inicial.
    """
    flask_session.pop('user_id', None)
    flask_session.pop('user_class', None)
    return redirect(url_for('home'))

@app.route('/perfil')
def perfil():
    """
    Rota que exibe o perfil do usuário logado, incluindo seus filmes favoritos e avaliações recentes.

    Retorna:
        Template: O template perfil.html com os dados do usuário.
    """
    if 'user_id' in flask_session:
        user_id = flask_session['user_id']
        session_db = Session()

        try:
            reviews = session_db.query(Avaliacao).filter_by(UserName=user_id).all()
            recent_reviews = []
            for review in reviews:
                id_filme = review.id_filme
                url_filme = f'https://api.themoviedb.org/3/movie/{id_filme}?api_key={API_KEY}'
                filme_response = requests.get(url_filme)
                if filme_response.status_code == 200:
                    filme = filme_response.json()
                    recent_reviews.append(filme)

            favoritos = session_db.query(ListaFavoritos).filter_by(userName=user_id).all()
            filmes_favoritos = []
            for favorito in favoritos:
                movie_id = favorito.movie_id
                movie_url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}'
                movie_response = requests.get(movie_url)
                if movie_response.status_code == 200:
                    movie = movie_response.json()
                    filmes_favoritos.append(movie)
        except:
            flash('Error loading favorite movies or recent reviews', 'error')
            return redirect(url_for('login'))
        finally:
            session_db.close()

        return render_template('perfil.html', usuario=flask_session['user_id'], classe=flask_session['user_class'], favorito=filmes_favoritos, recent_reviews=recent_reviews)
    else:
        return redirect(url_for('login'))

@app.route('/add_to_favorites', methods=['POST'])
def add_to_favorites():
    """
    Rota que adiciona ou remove um filme dos favoritos do usuário.

    Retorna:
        JSON: O status da operação ('added' ou 'removed').
    """
    user_id = flask_session['user_id']
    if 'user_id' in flask_session:
        user_id = flask_session['user_id']
        data = request.get_json()
        movie_id = data.get('movie_id')
        if movie_id:
            session_db = Session()
            favorite = session_db.query(ListaFavoritos).filter_by(userName=user_id, movie_id=movie_id).first()
            if favorite:
                session_db.delete(favorite)
                session_db.commit()
                status = 'removed'
            else:
                favorite = ListaFavoritos(userName=user_id, movie_id=movie_id)
                session_db.add(favorite)
                session_db.commit()
                status = 'added'

                # Recalculate user class if a multiple of 7 favorites
                total_favorites = session_db.query(ListaFavoritos).filter_by(userName=user_id).count()
                if total_favorites % 7 == 0:
                    user = session_db.query(User).filter_by(UserName=user_id).first()
                    user_class = User_Class(user.Class)
                    favorites = session_db.query(ListaFavoritos).filter_by(userName=user_id).all()
                    favorite_movies = []
                    for fav in favorites:
                        movie_url = f'https://api.themoviedb.org/3/movie/{fav.movie_id}?api_key={API_KEY}'
                        movie_response = requests.get(movie_url)
                        if movie_response.status_code == 200:
                            movie = movie_response.json()
                            favorite_movies.append(movie)
                    user_class.calculate_user_class(favorite_movies)
                    user.Class = user_class.class_user
                    session_db.commit()
                    flask_session['user_class'] = user_class.class_user

            session_db.close()
            return jsonify({'status': status})
    else:
        return jsonify({'status': 'You must be logged in to favorite a movie'})


@app.route('/rate_movie', methods=['POST'])
def rate_movie():
    """
    Rota que permite ao usuário avaliar um filme.

    Retorna:
        JSON: O status da operação ('rated') e a nova avaliação.
    """
    if 'user_id' in flask_session:
        user_id = flask_session['user_id']
        data = request.get_json()
        movie_id = data.get('movie_id')
        rating = int(data.get('rating'))
        comentario = data.get('comentario')

        if movie_id and rating:
            session_db = Session()
            user_rating = session_db.query(Avaliacao).filter_by(id_filme=movie_id, UserName=user_id).first()
            if user_rating:
                user_rating.stars = rating
                user_rating.comentario = comentario
            else:
                user_rating = Avaliacao(UserName=user_id, id_filme=movie_id, stars=rating, comentario=comentario)
                session_db.add(user_rating)
            session_db.commit()
            session_db.close()
            return jsonify({'status': 'rated', 'new_rating': rating})
    return jsonify({'status': 'error'})

@app.route('/delete_rating', methods=['POST'])
def delete_rating():
    """
    Rota que permite ao usuário deletar uma avaliação.

    Retorna:
        JSON: O status da operação ('message' ou 'error').
    """
    if 'user_id' not in flask_session:
        return jsonify({'error': 'You must be logged in to delete a rating.'}), 401

    data = request.get_json()
    movie_id = data.get('movie_id')
    user_id = flask_session['user_id']

    if not movie_id:
        return jsonify({'error': 'Invalid data.'}), 400

    session_db = Session()
    try:
        user_rating = session_db.query(Avaliacao).filter_by(id_filme=movie_id, UserName=user_id).first()
        if user_rating:
            session_db.delete(user_rating)
            session_db.commit()
            return jsonify({'message': 'Rating deleted successfully!'})
        else:
            return jsonify({'error': 'Rating not found.'}), 404
    except IntegrityError:
        session_db.rollback()
        return jsonify({'error': 'An error occurred.'}), 400
    finally:
        session_db.close()

socketio = SocketIO(app, cors_allowed_origins="*")
@socketio.on('message')
def handle_message(message):
    """
    Manipulador de mensagens recebidas pelo Socket.IO.

    Parâmetros:
        message (str): A mensagem recebida.
    """
    print("Received message: " + message)
    if message != "User connected!":
        send(message, broadcast=True)

@app.route('/message')
def index():
    """
    Rota que exibe a página de mensagens.
    """
    if 'user_id' in flask_session:
        username = flask_session['user_id']
    else:
        username = ''
    return render_template("message.html", username=username)

    
if __name__ == '__main__':
    app.run(debug=True, port=8001) # Executa o aplicativo Flask no modo debug
