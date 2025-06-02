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
from database import create_database, reset_tables, add_user, verify_user
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
    discogs_client = get_client()
    options = []
    seen = set()

    try:
        releases = discogs_client.search(track=q, sort="score", type="release", per_page=10)
    except Exception as e:
        print(f"⚠️ Matching error: {e}")

    print(f"releases type {type(releases)}")
    print(f"releases length: {len(releases)}")
    for release in releases:
        print(release)
        print(type(release))

        wait()
        try:
            rel = discogs_client.release(release.id)
        except:
            print(f"Warning: no details found for {release.id}")
            continue
        try:
            for i, t in enumerate(rel.tracklist or []):
                if is_remix(t.title):
                    continue
                if clean_string(q) in clean_string(t.title) and t.title not in seen:
                    seen.add(t.title)
                    artist = ', '.join(a.name for a in rel.artists) if rel.artists else "Unknown Artist"
                    album = rel.title or "Unknown Album"
                    label = f"{t.title} by {artist} (Album: {album}) | release id: {rel.id}"
                    options.append(label)
                    if len(options) >= 10:
                        return options
        except Exception as e:
            print(f"Warning:{e}")
            continue
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

            payload = caesar_decrypt(data.decode()).strip()

            payload_dict = json.loads(payload)
            msg = payload_dict.get("msg")
            msg_type = payload_dict.get("msg_type")
            print(f"🔍 Received query: {msg}")
            print(msg_type)

            # identify message as matches call
            if msg_type == "options":
                results = get_matching_songs(msg)
                response_json = json.dumps(results)

            elif msg_type == "matches":
                results = get_best_matches(int(msg))
                response_json = json.dumps(results)

            elif msg_type == "signup":
                response = add_user(
                    msg.get("username"),
                    msg.get("password")
                )
                print(response)
                response_json = json.dumps(response)

            elif msg_type == "login":
                response = verify_user(
                    msg.get("username"),
                    msg.get("password")
                )
                response_json = json.dumps(response)

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




