from utils.utilities import clean_string

class ArtistDetails:
    def __init__(self, artist_name):
        self.artist_name = artist_name
        self.artist_clean_name = clean_string(artist_name)  # שם נקי להשוואה

    def __str__(self):
        return f"{self.artist_name}"
