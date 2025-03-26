class SongDetails:
    """ song details """
    def __init__(self, title, year, country, styles="none"):
        self.title = title
        self.year = year,
        self.country = country,
        self.styles = styles

    def __str__(self):
        return f"{self.title}, ({self.year})"