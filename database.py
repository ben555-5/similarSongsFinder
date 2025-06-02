import sqlite3
import json
import hashlib
from datetime import datetime
from song_details_class import SongDetails
from artist_details_class import ArtistDetails
import os

# Use consistent absolute DB path
DATABASE_NAME = os.path.join(os.path.dirname(__file__), "song_database.db3")

# Create all database tables
def create_database():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # Songs table
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

    # Artists table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS artists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            artist_name TEXT NOT NULL,
            clean_artist_name TEXT NOT NULL UNIQUE
        )
    ''')

    # Song-artists link table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS song_artists_link (
            song_id INTEGER NOT NULL,
            artist_id INTEGER NOT NULL,
            PRIMARY KEY (song_id, artist_id),
            FOREIGN KEY (song_id) REFERENCES songs(id) ON DELETE CASCADE,
            FOREIGN KEY (artist_id) REFERENCES artists(id) ON DELETE CASCADE
        )
    ''')

    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        )
    ''')

    # Search logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS search_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            song_id INTEGER NOT NULL,
            timestamp TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(song_id) REFERENCES songs(id)
        )
    ''')

    conn.commit()
    conn.close()

# Add a new song to the database
def add_song(song_details: SongDetails):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    res = cursor.execute('''
        SELECT id FROM songs WHERE clean_song_name = ? AND song_year = ?
    ''', (song_details.clean_title, song_details.year)).fetchone()

    if res:
        song_id = res[0]
    else:
        cursor.execute('''
            INSERT INTO songs (song_name, clean_song_name, song_year, song_style, song_region)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            song_details.title,
            song_details.clean_title,
            song_details.year,
            json.dumps(song_details.styles),
            song_details.country
        ))
        song_id = cursor.lastrowid

    conn.commit()
    conn.close()
    return song_id

# Add a new artist to the database
def add_artist(artist_details: ArtistDetails):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    res = cursor.execute('''
        SELECT id FROM artists WHERE clean_artist_name = ?
    ''', (artist_details.artist_clean_name,)).fetchone()

    if res:
        artist_id = res[0]
    else:
        cursor.execute('''
            INSERT INTO artists (artist_name, clean_artist_name)
            VALUES (?, ?)
        ''', (
            artist_details.artist_name,
            artist_details.artist_clean_name
        ))
        artist_id = cursor.lastrowid

    conn.commit()
    conn.close()
    return artist_id

# Link a song to an artist
def link_song_to_artist(song_id: int, artist_id: int):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO song_artists_link (song_id, artist_id)
        VALUES (?, ?)
    ''', (song_id, artist_id))
    conn.commit()
    conn.close()

# Build SongDetails object from DB row
def construct_song_details(name, year, region, style_json):
    styles = json.loads(style_json) if style_json else []
    return SongDetails(title=name, year=year, country=region, styles=styles)

# Get all songs except those in exclude_list
def get_all_songs(exclude_list):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT id, song_name, song_year, song_style, song_region FROM songs")
    rows = cursor.fetchall()

    songs = []
    for id, name, year, style_json, region in rows:
        if id in exclude_list:
            continue
        songs.append(construct_song_details(name, year, region, style_json))

    conn.close()
    return songs

# Get song by its database ID
def get_song_by_id(song_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT song_name, song_year, song_region, song_style FROM songs WHERE id = ?", (song_id,))
    row = cursor.fetchone()
    song = construct_song_details(row[0], row[1], row[2], row[3])

    conn.close()
    return song

# Reset all tables (clears data)
def reset_tables():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM songs")
    cursor.execute("DELETE FROM artists")
    cursor.execute("DELETE FROM song_artists_link")
    cursor.execute("DELETE FROM users")
    cursor.execute("DELETE FROM search_logs")

    cursor.execute("DELETE FROM sqlite_sequence WHERE name='songs'")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='artists'")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='users'")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='search_logs'")

    conn.commit()
    conn.close()
    print("🔁 Tables reset and ID counters cleared.")


def add_user(username, password):
    """ User signup """
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def verify_user(username, password):
    """ User Login """
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ? AND password_hash = ?", (username, password_hash))
    result = cursor.fetchone()
    conn.close()
    if result[0]:
        return result[0][0]
    return -1

# Log a user's song confirmation
def log_search(user_id, song_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    timestamp = datetime.now().isoformat()
    cursor.execute('''
        INSERT INTO search_logs (user_id, song_id, timestamp)
        VALUES (?, ?, ?)
    ''', (user_id, song_id, timestamp))
    conn.commit()
    conn.close()


def init():
    create_database()




