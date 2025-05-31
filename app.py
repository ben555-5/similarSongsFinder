import socket
import threading
import time
import re
import json

from discogs_lib import get_client
from collector import collect_popular_songs
from song_details_class import SongDetails
from utils.utilities import clean_string
from utils.caesar_cipher import caesar_decrypt, caesar_encrypt
from database import create_database, reset_tables
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
    try:
        for r in d.search(track=q, sort="score", type="release", per_page=10):
            wait()
            try:
                rel = d.release(r.id)
            except:
                continue
            for i, t in enumerate(rel.tracklist or []):
                if is_remix(t.title):
                    continue
                if clean_string(q) in clean_string(t.title) and t.title not in seen:
                    seen.add(t.title)
                    artist = ', '.join(a.name for a in rel.artists) if rel.artists else "Unknown Artist"
                    album = rel.title or "Unknown Album"
                    label = f"{t.title} by {artist} (Album: {album})"
                    options.append(label)
                    if len(options) >= 10:
                        return options
    except Exception as e:
        print(f"⚠️ Matching error: {e}")
    return options


def run_collector_loop():
    while True:
        print("🔁 Running song collector...")
        try:
            collect_popular_songs(limit=50)
        except Exception as e:
            print(f"⚠️ Collector error: {e}")
        time.sleep(600)  # 10 minutes


def handle_client(conn, addr):
    print(f"✅ Connected from {addr}")
    try:
        while True:
            data = conn.recv(65536)
            if not data:
                break

            msg = caesar_decrypt(data.decode()).strip()
            print(f"🔍 Received query: {msg}")

            results = get_matching_songs(msg)
            response_json = json.dumps(results)
            encrypted = caesar_encrypt(response_json)
            conn.sendall(encrypted.encode())

    except Exception as e:
        print(f"❌ Client error: {e}")
    finally:
        conn.close()
        print(f"🔌 Disconnected from {addr}")

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"🚀 Server running at {HOST}:{PORT}")
        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    threading.Thread(target=run_collector_loop, daemon=True).start()
    start_server()




