from utils.utilities import clean_string


class SongDetails:
    def __init__(self, title, year, country, styles=None, release_id=None):
        self.title = title
        self.clean_title = clean_string(title)
        self.year = year
        self.country = country or "Unknown"
        self.styles = styles
        self.release = release_id

    def __str__(self):
        return f"{self.title}, ({self.year})"


