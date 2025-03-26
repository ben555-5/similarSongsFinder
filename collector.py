#region imports

import discogs_client
import re
from song_details_class import SongDetails
from database import add_song, init

#endregion imports

#region global variables

init()
song_list = []
d = discogs_client.Client('ExampleApplication/0.1', user_token="GVOasQPZopgGnCjiQpCQlsbIsvocZxzMkEsJNURq")

#endregion global variables

#region functions

def clean_string(s: str) -> str:
    # Convert to lowercase
    s = s.lower()

    # Remove quotes
    s = re.sub(r'[\'\u2019"]', '', s)

    # Remove everything inside parentheses (including the parentheses themselves)
    s = re.sub(r'\(.*?\)', '', s)

    # Replace any sequence of separators (non-word characters) with a single underscore
    s = re.sub(r'[^\w]+', '_', s)

    # Remove leading and trailing underscores
    s = s.strip('_')

    return s

def collect_popular_songs():
    Budget = 5
    results = d.search(type="release", sort="hot")
    for result in results:
        for track in result.tracklist:
            tmp_song = SongDetails(
                title=track.title,
                year=result.year,
                country=result.country,
                styles= result.styles
            )

            song = {
                "title": tmp_song.title,
                "clean_title": clean_string(tmp_song.title),
                "release_year": tmp_song.year,
                "country": tmp_song.country,
                "styles": tmp_song.styles
            }
            add_song(tmp_song)
        Budget -= 1
        if Budget == 0:
            break





#endregion functions

#region main
collect_popular_songs()
print(song_list)

#endregion main