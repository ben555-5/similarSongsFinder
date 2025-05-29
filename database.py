import sqlite3
import json
from song_details_class import SongDetails
from artist_details_class import ArtistDetails

# שם קובץ מסד הנתונים
DATABASE_NAME = "song_database.db3"

# פונקציה ליצירת הטבלאות במסד אם הן לא קיימות
def create_database():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # טבלת שירים
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

    # טבלת אמנים
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS artists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            artist_name TEXT NOT NULL,
            clean_artist_name TEXT NOT NULL UNIQUE
         )
    ''')

    # טבלת קישור בין שירים לאמנים
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

# פונקציה להוספת שיר למסד הנתונים
def add_song(song_details: SongDetails):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # בדיקה אם השיר כבר קיים לפי שם נקי ושנה
    res = cursor.execute('''
        SELECT id FROM songs
        WHERE clean_song_name = ? AND song_year = ?
    ''', (song_details.clean_title, song_details.year)).fetchone()

    if res:
        song_id = res[0]
    else:
        # הוספת שיר חדש למסד
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

# פונקציה להוספת אמן למסד הנתונים
def add_artist(artist_details: ArtistDetails):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # בדיקה אם האמן כבר קיים לפי שם נקי
    res = cursor.execute('''
        SELECT id FROM artists WHERE clean_artist_name = ?
    ''', (artist_details.artist_clean_name,)).fetchone()

    if res:
        artist_id = res[0]
    else:
        # הוספת אמן חדש
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

# פונקציה לקישור שיר לאמן בטבלת הקישור
def link_song_to_artist(song_id: int, artist_id: int):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # הכנסת קישור אם הוא לא קיים כבר
    cursor.execute('''
        INSERT OR IGNORE INTO song_artists_link (song_id, artist_id)
        VALUES (?, ?)
    ''', (song_id, artist_id))

    conn.commit()
    conn.close()

# פונקציה לבניית אובייקט SongDetails מתוך פרטי השיר במסד
def construct_song_details(name, year, region, style_json):
    styles = json.loads(style_json) if style_json else []
    song = SongDetails(title=name, year=year, country=region, styles=styles)
    return song

# קבלת כל השירים, פרט לאלו שמופיעים ברשימת החרגה
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

# שליפת שיר לפי מזהה
def get_song_by_id(song_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT song_name, song_year, song_region, song_style FROM songs WHERE id = ?", (song_id,))
    row = cursor.fetchone()
    song = construct_song_details(row[0], row[1], row[2], row[3])

    conn.close()
    return song

# פונקציה לאיפוס הטבלאות במסד
def reset_tables():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # מחיקת כל הנתונים מכל הטבלאות
    cursor.execute("DELETE FROM songs")
    cursor.execute("DELETE FROM artists")
    cursor.execute("DELETE FROM song_artists_link")

    # איפוס מונה ה-ID (המספר הרץ)
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='songs'")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='artists'")

    conn.commit()
    conn.close()
    print("Tables reset and ID counters cleared.")

# אתחול בסיס הנתונים (יצירת טבלאות)
def init():
    create_database()


