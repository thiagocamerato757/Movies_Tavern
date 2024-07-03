class User_Class:
    def __init__(self, class_user=None):
        if class_user:
            self.class_user = class_user
        else:
            self.class_user = "Peasant"

    def calculate_user_class(self, favorite_movies):
        """
        Calcula a classe RPG do usuário com base nos gêneros de seus filmes favoritos.

        Parâmetros:
            favorite_movies (list): Uma lista de dicionários, onde cada dicionário representa um filme com seus gêneros.

        Esta função percorre os filmes favoritos do usuário, conta a ocorrência de cada gênero e determina a classe RPG 
        do usuário com base no gênero mais frequente. A classe do usuário é atualizada para a classe RPG correspondente.
        """
        genre_count = {rpg_class: 0 for rpg_class in genre_map.keys()}
        
        for movie in favorite_movies:
            movie_genres = movie.get('genres', [])
            for genre in movie_genres:
                genre_name = genre['name']
                for rpg_class, genres in genre_map.items():
                    if genre_name in genres:
                        genre_count[rpg_class] += 1

        new_class = max(genre_count, key=genre_count.get)
        self.class_user = new_class

genre_map = {
    "Warrior": ["Action","Thriller"], #Guerreiro
    "Wizard": ["Fantasy","Science Fiction"], #Mago
    "Rogue": ["Crime", "Mystery", "Horror"], #Ladino
    "Cleric": ["Drama", "History","Documentary"], #Clérigo
    "Barbarian": ["War", "Western"], #Bárbaro
    "Druid": ["Animation", "TV Movie"], #Druida
    "Bard": ["Music", "Romance", "Comedy"], #Bardo
    "Paladin": ["Family","Adventure"] #Paladino
}

# Lista de filmes de exemplo para retornar "Paladino", mas misturando gêneros
favorite_movies = [
    {'genres': [{'id': 878, 'name': 'Science Fiction'}, {'id': 16, 'name': 'Animation'}]}, # Paladino, Druida
    {'genres': [{'id': 10751, 'name': 'Family'}, {'id': 14, 'name': 'Fantasy'}]},         # Paladino, Mago
    {'genres': [{'id': 99, 'name': 'Documentary'}, {'id': 28, 'name': 'Action'}]},        # Mago, Guerreiro
    {'genres': [{'id': 14, 'name': 'Fantasy'}, {'id': 99, 'name': 'Documentary'}]},       # Mago
    {'genres': [{'id': 10751, 'name': 'Family'}, {'id': 18, 'name': 'Drama'}]},           # Paladino, Clérigo
    {'genres': [{'id': 878, 'name': 'Science Fiction'}, {'id': 12, 'name': 'Adventure'}]},# Paladino, Bárbaro
    {'genres': [{'id': 878, 'name': 'Science Fiction'}, {'id': 10751, 'name': 'Family'}]} # Paladino
]

# Instanciando e calculando a classe do usuário
user_class = User_Class()
user_class.calculate_user_class(favorite_movies)
print(user_class.class_user)  # Deve retornar "Paladino"
