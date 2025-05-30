HOST = '127.0.0.1'
PORT = 65432
DELAY = 1.25

import socket
import threading
import time
import re
import json

from discogs_lib import get_client
from song_details_class import SongDetails
from utils.utilities import clean_string
from utils.caesar_cipher import caesar_decrypt, caesar_encrypt
from database import add_song, reset_tables
from similar_song_lib import get_best_matches
from collector import collect_popular_songs

# Server settings
HOST = '127.0.0.1'
PORT = 65432
DELAY = 1.25

# Wait between Discogs API calls
def wait():
    time.sleep(DELAY)

# Check if title is likely a remix
def is_remix(title: str) -> bool:
    brackets = re.findall(r'[\(\[].*?[\)\]]', title.lower())
    keywords = ["remix", "edit", "version", "mix", "rework", "dub", "acoustic"]
    return any(k in b for b in brackets for k in keywords)

# Get up to 10 matching songs from Discogs
def get_matching_songs(q):
    d, options, seen = get_client(), [], set()
    try:
        for r in d.search(track=q, sort="score", type="release", per_page=10):
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
    except Exception as e:
        print(f"⚠️ Matching error: {e}")
    return options

# Add the selected song and get similar matches
def find_similar_songs(release_id, track_index):
    d = get_client()
    try:
        release = d.release(int(release_id))
        track = release.tracklist[int(track_index)]
    except Exception as e:
        print(f"❌ Error loading track: {e}")
        return ["❌ Failed to add song."]

    song = SongDetails(
        title=track.title,
        year=release.year,
        country=release.country or "Unknown",
        styles=release.styles or []
    )
    song_id = add_song(song)
    results = get_best_matches(song_id)
    return [f"{str(r[0])} | {r[1]}" for r in results]

# Handle one client connection
def handle_client(conn, addr):
    print(f"✅ Connected from {addr}")
    try:
        while True:
            msg = caesar_decrypt(conn.recv(65536).decode())
            if not msg:
                break

            if msg.startswith("SEARCH:"):
                query = msg[7:]
                print(f"🔍 Searching for: {query}")
                options = caesar_encrypt(get_matching_songs(query))
                conn.sendall(json.dumps(options).encode())

            # elif msg.startswith("CONFIRM:"):
            #     track_id = msg[8:]
            #     print(f"🎯 Confirmed track: {track_id}")
            #     rel_id, trk_id = track_id.split("|")
            #     matches = caesar_encrypt(find_similar_songs(rel_id, trk_id))
            #     conn.sendall(json.dumps(matches).encode())

    except Exception as e:
        print(f"❌ Client error: {e}")
    finally:
        conn.close()
        print(f"🔌 Disconnected from {addr}")

# TCP socket server
def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"🚀 Server running at {HOST}:{PORT}")
        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

# Collector loop in background
def run_collector_loop():
    while True:
        time.sleep(60)  # 1 minute
        print("🔁 Running song collector...")
        try:
            collect_popular_songs(limit=50)
        except Exception as e:
            print(f"⚠️ Collector error: {e}")

# Main
if __name__ == "__main__":
    reset_tables()
    threading.Thread(target=run_collector_loop, daemon=True).start()
    start_server()
