import librosa
import os
from tinytag import OtherFields, TinyTag

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
track.year = tag.year
track_genre = tag.genre
track_duration = tag.duration

print(f"Tempo: {str(tempo)} BPM")
print(f'This track is called {tag.title}')
print(f'This track was released in {tag.year} ')
print(f"This track's genre is {tag.genre} ")
print(f'It is {tag.duration:.2f} seconds long.')

def filter_track(track):
    ref_track_title = track.tag.title
    ref_track.year = track.tag.year
    ref_track_genre = track.tag.genre
    ref_track_duration = track.tag.duration

# artist: str | None = tag.artist
# additional_artists: list[str] | None = tag.other.get('artist')
# print(f'this song was made by:{artist}')
# print(f'features:{additional_artists}')
# tag.other.get()
# C:\Users\Student\Downloads\youtube_c6FImLFrPI8_audio.mp3