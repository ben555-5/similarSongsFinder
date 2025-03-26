import sqlite3
from song_details_class import SongDetails


DATABASE_NAME = "song_database.db3"
def create_database():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS songs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            song_name TEXT NOT NULL,
            song_year INTEGER NOT NULL,
            song_style TEXT NOT NULL,
            song_region TEXT NOT NULL
        )
    ''')


def add_song(song_details : SongDetails):
    # Connect to the database
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # Insert the song into the table
    cursor.execute('''
        INSERT INTO songs (song_name, song_year, song_style, song_region)
        VALUES (?, ?, ?, ?)
    ''', (song_details.title, song_details.year, song_details.styles, song_details.country))

    # Commit and close connection
    conn.commit()
    conn.close()


def init():
    create_database()

