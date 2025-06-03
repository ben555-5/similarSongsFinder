#region imports

# Import Discogs API client and supporting exceptions
from discogs_lib import get_client
import time
from discogs_client.exceptions import HTTPError
from json.decoder import JSONDecodeError

# Import data classes for songs and artists
from song_details_class import SongDetails
from artist_details_class import ArtistDetails

# Import database functions
from database import (
    init,
    reset_tables,
    add_song,
    add_artist,
    link_song_to_artist
)

#endregion

#region global setup

# Initialize the database
init()

# Create a Discogs API client instance
d = get_client()

# endregion

# region main logic


def collect_popular_songs(limit):
    # Search for popular releases from Discogs
    results = d.search(type="release", sort="hot", per_page=50)
    count = 0

    for rel in results:
        if count >= limit:
            break

        try:
            # Get full release details by ID
            release = d.release(rel.id)

            for track in release.tracklist:
                time.sleep(0.1)  # Sleep to respect API rate limits

                # Create a SongDetails object and add to database
                song = SongDetails(
                    title=track.title,
                    year=release.year,
                    country=release.country,
                    styles=release.styles,
                    release_id=release.id
                )
                song_id = add_song(song)

                # Iterate over all artists in the release
                for artist in release.artists:
                    try:
                        # (Optional) fetch additional artist info
                        artist_info = d.artist(artist.id)

                        artist_details = ArtistDetails(artist.name)
                        artist_id = add_artist(artist_details)

                        if artist_id:
                            link_song_to_artist(song_id, artist_id)

                    except HTTPError as e:
                        if e.status_code == 429:
                            print("⏳ Rate limit hit — waiting 5 seconds...")
                            time.sleep(5)
                        else:
                            print(f"HTTP error for artist: {e}")
                    except JSONDecodeError:
                        print("⏳ JSON error while loading artist — waiting...")
                        time.sleep(5)

            count += 1

        except HTTPError as e:
            if e.status_code == 429:
                print("⏳ Rate limit hit — waiting 5 seconds...")
                time.sleep(5)
            else:
                print(f"HTTP error for release: {e}")
        except JSONDecodeError:
            print("⏳ JSON error while loading release — waiting...")
            time.sleep(5)

# endregion


# region entry point


if __name__ == "__main__":
    collect_popular_songs(limit=1000)

# endregion

