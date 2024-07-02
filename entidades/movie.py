class Movie:
    def __init__(self, movie_data, cast, comments, average_rating):
        self.id = movie_data['id']
        self.title = movie_data['title']
        self.poster_path = movie_data['poster_path']
        self.overview = movie_data.get('overview', '')
        self.cast = cast
        self.comments = comments
        self.average_rating = average_rating