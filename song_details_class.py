from utilities import clean_string


class SongDetails:
    """ song details """
    def __init__(self, title, year, country, styles="none"):
        self.title = title
        self.clean_title = clean_string(title)
        self.year = year
        self.country = country or "Unknown"
        self.styles = styles

    def __str__(self):
        return f"{self.title}, ({self.year})"

