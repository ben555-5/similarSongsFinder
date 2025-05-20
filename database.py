import sqlite3
import json
from song_details_class import SongDetails
from artist_details_class import ArtistDetails





DATABASE_NAME = "song_database.db3"
def create_database():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS songs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            song_name TEXT NOT NULL,
            clean_song_name TEXT NOT NULL,
            song_year INTEGER NOT NULL,
            song_style TEXT NOT NULL,
            song_region TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS artists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            artist_name TEXT NOT NULL,
            clean_artist_name TEXT NOT NULL UNIQUE
         )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS song_artists_link (
            song_id INTEGER NOT NULL,
            artist_id INTEGER NOT NULL,
            PRIMARY KEY (song_id, artist_id),
            FOREIGN KEY (song_id) REFERENCES songs(id) ON DELETE CASCADE,
            FOREIGN KEY (artist_id) REFERENCES artists(id) ON DELETE CASCADE
        )
    ''')



def add_song(song_details: SongDetails):
    # Connect to the database
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # Insert the song into the table
    cursor.execute('''
        INSERT INTO songs (song_name, clean_song_name, song_year, song_style, song_region)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        song_details.title,
        song_details.clean_title,
        song_details.year,
        json.dumps(song_details.styles),
        song_details.country))

    res = cursor.execute('''
        SELECT last_insert_rowid()
    ''')
    id = res.fetchone()[0]

    # Commit and close connection
    conn.commit()
    conn.close()

    return id



def add_artist(artist_details: ArtistDetails):
    # Connect to the database
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # Insert the artist into the table
    cursor.execute('''
        INSERT INTO artists (artist_name, clean_artist_name)
         VALUES (?, ?)
        ON CONFLICT(clean_artist_name) DO NOTHING
        
    ''', (
        artist_details.artist_name,
        artist_details.artist_clean_name
    ))
    res = cursor.execute('''
    SELECT id FROM artists WHERE clean_artist_name = ?
    ''', (
        artist_details.artist_clean_name
    ))
    print(res.fetchone())
    # Commit and close connection
    conn.commit()
    conn.close()


def reset_tables():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # Delete all records from songs and artists
    cursor.execute("DELETE FROM songs")
    cursor.execute("DELETE FROM artists")

    # Reset the auto-increment counters
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='songs'")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='artists'")

    conn.commit()
    conn.close()
    print("Tables reset and ID counters cleared.")


def init():
    create_database()

