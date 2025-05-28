from datetime import datetime

class SearchLog:
    def __init__(self, user_id, song_id, timestamp=None):
        self.user_id = user_id
        self.song_id = song_id
        self.timestamp = timestamp or datetime.now()