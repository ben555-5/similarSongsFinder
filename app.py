import socket
import threading
import time
import re
import json

from discogs_lib import get_client
from song_details_class import SongDetails
from utilities import clean_string
from database import add_song, reset_tables
from similar_song_lib import get_best_matches

HOST = '127.0.0.1'
PORT = 65432
DELAY = 1.25

def wait():
    time.sleep(DELAY)

def is_remix(title: str) -> bool:
    brackets = re.findall(r'[\(\[].*?[\)\]]', title.lower())
    keywords = ["remix", "edit", "version", "mix", "rework", "dub", "acoustic"]
    return any(k in b for b in brackets for k in keywords)

def get_matching_songs(q):
    d, options, seen = get_client(), [], set()
    for r in d.search(track=q, sort="score", type="release", per_page=50):
        wait()
        try: rel = d.release(r.id)
        except: continue
        for i, t in enumerate(rel.tracklist or []):
            if is_remix(t.title): continue
            if clean_string(q) in clean_string(t.title) and t.title not in seen:
                seen.add(t.title)
                artist = ', '.join(a.name for a in rel.artists) if rel.artists else "Unknown Artist"
                album = rel.title or "Unknown Album"
                label = f"{t.title} by {artist} (Album: {album})"
                options.append((f"{rel.id}|{i}", label))
                if len(options) >= 10: return options
    return options

def find_similar_songs(release_id, track_index):
    d = get_client()
    release = d.release(int(release_id))
    track = release.tracklist[int(track_index)]
    song = SongDetails(
        title=track.title,
        year=release.year,
        country=release.country or "Unknown",
        styles=release.styles or []
    )
    song_id = add_song(song)
    results = get_best_matches(song_id)
    return [f"{str(r[0])} | {r[1]}" for r in results]

def handle_client(conn, addr):
    print(f"✅ Connected from {addr}")
    try:
        while True:
            msg = conn.recv(8192).decode()
            if msg.startswith("SEARCH:"):
                query = msg[7:]
                options = get_matching_songs(query)
                conn.sendall(json.dumps(options).encode())
            elif msg.startswith("CONFIRM:"):
                track_id = msg[8:]
                rel_id, trk_id = track_id.split("|")
                matches = find_similar_songs(rel_id, trk_id)
                conn.sendall(json.dumps(matches).encode())
    except Exception as e:
        print("Client error:", e)
    finally:
        conn.close()

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"🚀 Server running on {HOST}:{PORT}")
        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    reset_tables()
    start_server()
