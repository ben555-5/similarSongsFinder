#region imports

from discogs_lib import get_client
import time
from discogs_client.exceptions import HTTPError
from json.decoder import JSONDecodeError

from song_details_class import SongDetails
from artist_details_class import ArtistDetails
from database import (
    init,
    reset_tables,
    add_song,
    add_artist,
    link_song_to_artist
)

#endregion

#region global setup

init()
d = get_client()

#endregion

#region main logic

def collect_popular_songs(limit):
    results = d.search(type="release", sort="hot")
    count = 0

    for partial_release in results:
        if count >= limit:
            break

        try:
            # Re-fetch full release with all details including artists
            release = d.release(partial_release.id)

            for track in release.tracklist:
                time.sleep(0.1)  # Avoid hitting rate limit

                song = SongDetails(
                    title=track.title,
                    year=release.year,
                    country=release.country,
                    styles=release.styles
                )
                song_id = add_song(song)

                for artist in release.artists:
                    try:
                        # Optional: you can fetch full artist info here if needed
                        artist_info = d.artist(artist.id)  # to access more fields if wanted

                        artist_details = ArtistDetails(artist.name)
                        artist_id = add_artist(artist_details)

                        if artist_id:
                            link_song_to_artist(song_id, artist_id)

                    except HTTPError as e:
                        if e.status_code == 429:
                            print("⏳ Rate limit hit. Sleeping for 5 seconds...")
                            time.sleep(5)
                        else:
                            print(f"HTTP error for artist: {e}")
                    except JSONDecodeError:
                        print("⏳ JSON error while loading artist. Sleeping...")
                        time.sleep(5)

            count += 1

        except HTTPError as e:
            if e.status_code == 429:
                print("⏳ Rate limit hit. Sleeping for 5 seconds...")
                time.sleep(5)
            else:
                print(f"HTTP error for release: {e}")
        except JSONDecodeError:
            print("⏳ JSON error while loading release. Sleeping...")
            time.sleep(5)

#endregion

#region entry point

if __name__ == "__main__":
    reset_tables()
    collect_popular_songs(limit=1000)

#endregion