class User_Class:
    def __init__(self, class_user=None):
        if class_user:
            self.class_user = class_user
        else:
            self.class_user = "Peasant"

    def calculate_user_class(self, favorite_movies):
        genre_count = {genre: 0 for genre in genre_map.keys()}
        for movie in favorite_movies:
            movie_genres = movie.get('genres', [])
            for genre in movie_genres:
                for rpg_class, genres in genre_map.items():
                    if genre in genres:
                        genre_count[rpg_class] += 1

        new_class = max(genre_count, key=genre_count.get)
        self.class_user = new_class

genre_map = {
    "Guerreiro": ["Action", "War"],
    "Mago": ["Fantasy"],
    "Ladino": ["Crime"],
    "Clérigo": ["Drama"],
    "Bárbaro": ["Adventure"],
    "Druida": ["Animation"],
    "Bardo": ["Music", "Romance"],
    "Paladino": ["Science Fiction"]
}
