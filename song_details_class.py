from utilities import clean_string


class SongDetails:
    """ song details """
    def __init__(self, title, year, artists, country, styles="none"):
        self.title = title
        self.clean_title = clean_string(title)
        self.year = year
        self.artists = artists
        clean_artist_list = [clean_string(item) for item in artists]
        self.clean_artists = clean_artist_list
        self.country = country
        self.styles = styles

    def __str__(self):
        return f"{self.title}, ({self.year})"

