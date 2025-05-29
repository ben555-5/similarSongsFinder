#region imports

# ייבוא לקוח API של Discogs
from discogs_lib import get_client
import time
from discogs_client.exceptions import HTTPError
from json.decoder import JSONDecodeError

# ייבוא מחלקות של שיר ואמן
from song_details_class import SongDetails
from artist_details_class import ArtistDetails

# ייבוא פונקציות לעבודה עם מסד הנתונים
from database import (
    init,
    reset_tables,
    add_song,
    add_artist,
    link_song_to_artist
)

#endregion

#region global setup

# אתחול בסיס הנתונים
init()

# יצירת מופע של לקוח Discogs
d = get_client()

#endregion

#region main logic

def collect_popular_songs(limit):
    # חיפוש של ריליסים פופולריים לפי Discogs
    results = d.search(type="release", sort="hot")
    count = 0

    for partial_release in results:
        if count >= limit:
            break

        try:
            # שליפה מלאה של ריליס לפי מזהה
            release = d.release(partial_release.id)

            for track in release.tracklist:
                time.sleep(0.1)  # השהייה כדי לא לעבור את מגבלת ה-API

                # יצירת מופע של שיר ושמירתו במסד הנתונים
                song = SongDetails(
                    title=track.title,
                    year=release.year,
                    country=release.country,
                    styles=release.styles
                )
                song_id = add_song(song)

                # מעבר על כל האומנים בריליס
                for artist in release.artists:
                    try:
                        # שליפה נוספת של מידע האמן (אם נרצה בעתיד)
                        artist_info = d.artist(artist.id)

                        artist_details = ArtistDetails(artist.name)
                        artist_id = add_artist(artist_details)

                        if artist_id:
                            link_song_to_artist(song_id, artist_id)

                    except HTTPError as e:
                        if e.status_code == 429:
                            print("⏳ חריגת קצב - המתנה של 5 שניות...")
                            time.sleep(5)
                        else:
                            print(f"שגיאת HTTP עבור אמן: {e}")
                    except JSONDecodeError:
                        print("⏳ שגיאת JSON בטעינת אמן - המתנה...")
                        time.sleep(5)

            count += 1

        except HTTPError as e:
            if e.status_code == 429:
                print("⏳ חריגת קצב - המתנה של 5 שניות...")
                time.sleep(5)
            else:
                print(f"שגיאת HTTP עבור ריליס: {e}")
        except JSONDecodeError:
            print("⏳ שגיאת JSON בטעינת ריליס - המתנה...")
            time.sleep(5)

#endregion

#region entry point

# כאשר הקובץ מופעל ישירות - איפוס הטבלאות והרצת האיסוף
if __name__ == "__main__":
    reset_tables()
    collect_popular_songs(limit=1000)

#endregion