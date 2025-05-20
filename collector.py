#region imports

import discogs_client
import time
from discogs_client.exceptions import HTTPError
from song_details_class import SongDetails
from database import add_song, add_artist, init, reset_tables
from artist_details_class import ArtistDetails
from json.decoder import JSONDecodeError

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
    results_iterator = iter(results)
    while True:
        try:
            result = next(results_iterator, None)
            if result is None:
                break;

        except HTTPError as e:
            if e.status_code == 429:
                print("⏳ Rate limit hit. Sleeping for 5 seconds...")
                time.sleep(5)
            else:
                print(f"HTTP error: {e.status_code} - {e}")
        except JSONDecodeError:
            print("⏳ Rate limit hit. Sleeping for 5 seconds...")
            time.sleep(5)


        for track in result.tracklist:
            time.sleep(0.1)
            tmp_song = SongDetails(
                title=track.title,
                year=result.year,
                country=result.country,
                styles=result.styles
                )
            song_id = add_song(tmp_song)


            artist_iter = iter(track.artists)
            while True:

                try:
                    artist = next(artist_iter, None)
                    if artist is None:
                        break
                    # Fetch full artist object from Discogs
                    artist_info = d.artist(artist.id)
                    print("---------------------", artist_info)

                except HTTPError as e:
                    if e.status_code == 429:
                        print("⏳ Rate limit hit. Sleeping for 5 seconds...")
                        time.sleep(5)
                    else:
                        print(f"HTTP error: {e.status_code} - {e}")
                except JSONDecodeError:
                    print("⏳ Rate limit hit. Sleeping for 5 seconds...")
                    time.sleep(5)

                # Create and store artist info
                artist_details = ArtistDetails(
                     artist_name=artist.name,
                )
                add_artist(artist_details)


        Budget -= 1
        if Budget == 0:
            break






#endregion functions

#region main
reset_tables()
collect_popular_songs()
print(song_list)

#endregion main