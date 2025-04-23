#region imports

import discogs_client
from song_details_class import SongDetails
from database import add_song, init
from utilities import clean_string

#endregion imports

#region global variables

init()
song_list = []
d = discogs_client.Client('ExampleApplication/0.1', user_token="GVOasQPZopgGnCjiQpCQlsbIsvocZxzMkEsJNURq")

#endregion global variables

#region functions


def collect_popular_songs():
    Budget = 5
    results = d.search(type="release", sort="hot")
    for result in results:
        for track in result.tracklist:

            tmp_song = SongDetails(
                title=track.title,
                year=result.year,
                artists=[str(item) for item in result.artists],
                country=result.country,
                styles=result.styles
            )

            add_song(tmp_song)
        Budget -= 1
        if Budget == 0:
            break





#endregion functions

#region main
collect_popular_songs()
print(song_list)

#endregion main