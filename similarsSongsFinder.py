import librosa
import os
from tinytag import TinyTag
import discogs_client
import re
from discogs_library import search_song_by_title
from youtube_search import YoutubeSearch
from pathlib import Path
import urllib.request
import argparse

youtube_url = ""
AUDIO_SAVE_DIRECTORY = "./audio"
results = YoutubeSearch(input("Search a song (youtube title): "), max_results=1).to_dict()
for v in results:
    youtube_url = 'https://www.youtube.com' + v['url_suffix']
    print(youtube_url)


# Detect tempo
tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
track_title = tag.title
track_year = tag.year
track_genre = tag.genre
track_duration = tag.duration
print(f"Downloaded and converted to MP3: {track_title}")

def remove_excess_tags(t_title):
    new_track_title = t_title
    new_track_title = re.sub(r"\(.*?\)", "", new_track_title)
    new_track_title = re.sub(r"\[.*?\]", "", new_track_title)
    new_track_title = re.sub(r"\|.*", "", new_track_title)
    return new_track_title


clean_name = remove_excess_tags(tag.title)


result = search_song_by_title(clean_name)
if result is None:
    exit()


song_data = {
    "tempo": str(tempo),
    "title": result.title,
    "release_year": result.year,
    "country": result.country,
    "duration": tag.duration,
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
# C:\Users\Student\Downloads\youtube_Vds8ddYXYZY_audio.mp3
