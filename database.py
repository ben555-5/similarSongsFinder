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
    conn.commit()
    conn.close()



def add_song(song_details: SongDetails):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # Check if the song already exists (based on clean name + year)
    res = cursor.execute('''
        SELECT id FROM songs
        WHERE clean_song_name = ? AND song_year = ?
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


def link_song_to_artist(song_id: int, artist_id: int):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # Insert the link; ignore if already linked (avoids duplicates)
    cursor.execute('''
        INSERT OR IGNORE INTO song_artists_link (song_id, artist_id)
        VALUES (?, ?)
    ''', (song_id, artist_id))

    conn.commit()
    conn.close()

def construct_song_details(name, year, region, style_json):
    styles = json.loads(style_json) if style_json else []
    song = SongDetails(title=name, year=year, country=region, styles=styles)
    return song


# exclude_list = list of song id's to exclude
def get_all_songs(exclude_list):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT id, song_name, song_year, song_style, song_region FROM songs")
    rows = cursor.fetchall()

    songs = []
    for id, name, year, style_json, region in rows:
        if (id in exclude_list):
            continue

        songs.append(construct_song_details(name, year, region, style_json))

    conn.close()
    return songs


def get_song_by_id(song_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT song_name, song_year, song_region, song_style FROM songs WHERE id = ?", (song_id,))
    row = cursor.fetchone()
    song = construct_song_details(row[0],row[1],row[2],row[3])

    conn.close()
    return song





def reset_tables():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # Delete all records from songs and artists
    cursor.execute("DELETE FROM songs")
    cursor.execute("DELETE FROM artists")
    cursor.execute("DELETE FROM song_artists_link")

    # Reset the auto-increment counters
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='songs'")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='artists'")

    conn.commit()
    conn.close()
    print("Tables reset and ID counters cleared.")


def init():
    create_database()

