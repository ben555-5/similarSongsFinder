import librosa
import os
from tinytag import TinyTag
import discogs_client
import re
from discogs_library import search_song_by_title

VALID_EXTENSIONS = {".mp3", ".wav"}

# Receive file path from user
while True:
    file_path = input("Please enter the path to your audio file: ")

    # Check if the file exists
    if not os.path.exists(file_path):
        print("Error: File does not exist. Please enter a valid file path.")
        continue

    # Check if the file extension is valid
    _, ext = os.path.splitext(file_path)
    if ext.lower() not in VALID_EXTENSIONS:
        print("Error: Invalid file format. Please enter a valid audio file (.mp3, .wav).")
        continue

    print("Valid file path received!")
    break

tag: TinyTag = TinyTag.get(file_path)

# Load audio file into librosa
y, sr = librosa.load(file_path)


# Detect tempo
tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
track_title = tag.title
track_year = tag.year
track_genre = tag.genre
track_duration = tag.duration


def remove_excess_tags(track_title):
    new_track_title = track_title
    new_track_title = re.sub(r"\(.*?\)", "", new_track_title)
    new_track_title = re.sub(r"\[.*?\]", "", new_track_title)
    new_track_title = re.sub(r"\|.*", "", new_track_title)
    return new_track_title


clean_name = remove_excess_tags(tag.title)


result = search_song_by_title(clean_name)
if result == None:
    exit()


song_data = {
    "tempo": str(tempo),
    "title": result.title,
    "release_year": result.year,
    "country": result.country,
    "duration":tag.duration,
    "styles": result.styles
}

print(song_data)


def filter_track(track):
    ref_track_title = track.tag.title
    ref_track_year = track.tag.year
    ref_track_genre = track.tag.genre
    ref_track_duration = track.tag.duration


# artist: str | None = tag.artist
# additional_artists: list[str] | None = tag.other.get('artist')
# print(f'this song was made by:{artist}')
# print(f'features:{additional_artists}')
# tag.other.get()
# d:\Users\Ben\Downloads\SNOOP DOGG - Conflicted feat. NAS  [Acapella-Vocals Only]  [91 BPM - Bm]  by EC13 - Acapella Boulevard.mp3
# d:\Users\Ben\Downloads\youtube_JGwWNGJdvx8_audio.mp3