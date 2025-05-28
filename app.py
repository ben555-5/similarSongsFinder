from flask import Flask, request, render_template_string, session
from discogs_lib import get_client
from song_details_class import SongDetails
from utilities import clean_string
from database import add_song, reset_tables
import time
import re
from similar_song_lib import get_best_matches
from collector import collect_popular_songs
import threading

app = Flask(__name__)
app.secret_key = 'your_secret_key'

DELAY = 1.25
COOLDOWN = 5
MAX = 20
SHOW = 10
last_call = [0]

HTML = '''
<!doctype html><title>Song Recommender</title>
<h2>Enter a Song Name</h2>
<form method="post">
  <input name="search_query" required>
  <input type="submit" value="Search">
</form>
{% if options %}
<h3>Select the song you meant:</h3>
<form method="post">
  {% for title, label in options %}
    <button name="confirmed_song" value="{{ title }}">{{ label }}</button><br>
  {% endfor %}
  <input type="submit" value="Next">
</form>
{% endif %}
{% if results %}
<h3>Top Matches:</h3>
<ul>
  {% for song in results %}
    <li>{{ song }}</li>
  {% endfor %}
</ul>
{% endif %}
'''

def wait():
    left = DELAY - (time.time() - last_call[0])
    if left > 0: time.sleep(left)
    last_call[0] = time.time()

def is_remix(title: str) -> bool:
    brackets = re.findall(r'[\(\[].*?[\)\]]', title.lower())
    keywords = ["remix", "edit", "version", "mix", "rework", "dub", "acoustic"]
    return any(k in b for b in brackets for k in keywords)

def score(song: SongDetails, q: str, rank: int):
    s = 0
    if clean_string(song.title) == clean_string(q): s += 30
    elif clean_string(q) in clean_string(song.title): s += 15
    s += max(0, (song.year - 1980) // 5)
    s += max(0, 100 - rank)
    return s

def get_matching_songs(q):
    d, options, seen = get_client(), [], set()
    try:
        for r in d.search(track=q, sort="score", type="release", per_page=50):
            wait()
            try: rel = d.release(r.id)
            except: continue
            for i, t in enumerate(rel.tracklist) or []:
                if is_remix(t.title): continue
                if clean_string(q) in clean_string(t.title) and t.title not in seen:
                    seen.add(t.title)
                    artist = ', '.join(a.name for a in rel.artists) if rel.artists else "Unknown Artist"
                    album = rel.title or "Unknown Album"
                    options.append((f"{rel.id}|{i}", f"{t.title} by {artist} (Album: {album})"))
                    if len(options) >= 10: return options
    except Exception as e:
        print(f"⚠️ Matching error: {e}")
    return options

def find_similar_songs(release_id, track_index):
    d = get_client()
    try:
        release = d.release(int(release_id))
    except Exception as e:
        print(f"❌ Error loading track: {e}")
        return ["❌ Failed to add song."]

    track = release.tracklist[int(track_index)]
    song = SongDetails(
        title=track.title,
        year=release.year,
        country=release.country or "Unknown",
        styles=release.styles or []
    )
    song_id = add_song(song)
    results = get_best_matches(song_id)
    return [f"{r[0].title} {r[1]}" for r in results]



@app.route('/', methods=['GET', 'POST'])
def index():
    res, opts, query = None, [], request.form.get('search_query', '').strip()
    if request.method == 'POST':
        if len(query) > 0 and len(query) < 4:
            res = ["❗ Enter at least 4 characters."]
        elif time.time() - session.get('last_time', 0) < COOLDOWN:
            res = ["⛔ Please wait before submitting again."]
        else:
            session['last_time'] = time.time()
            if 'confirmed_song' in request.form:
                track_id, song_id = request.form['confirmed_song'].split("|")
                res = find_similar_songs(track_id,song_id)
            elif query:
                opts = get_matching_songs(query)
                if not opts: res = ["No matches found. Try again."]

    return render_template_string(HTML, options=opts, results=res)

def run_collector_loop():
    while True:
        print("🔁 Running collector in background...")
        try:
            collect_popular_songs(limit=100)  # you can raise the limit if needed
        except Exception as e:
            print(f"⚠️ Collector error: {e}")
        time.sleep(600)  # 10 minutes = 600 seconds


if __name__ == '__main__':
    reset_tables()
    threading.Thread(target=run_collector_loop, daemon=True).start()
    app.run(debug=True)


