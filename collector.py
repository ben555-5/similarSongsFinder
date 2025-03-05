#region imports

import discogs_client

#endregion imports

#region global variables

song_list = []
d = discogs_client.Client('ExampleApplication/0.1', user_token="GVOasQPZopgGnCjiQpCQlsbIsvocZxzMkEsJNURq")

#endregion global variables

#region class's

class SongDetails:
    """ song details """
    def __init__(self, title, year, country, styles="none"):
        self.title = title
        self.year = year,
        self.country = country,
        self.styles = styles

    def __str__(self):
        return f"{self.title}, ({self.year})"

#endregion class's

#region functions

def collect_popular_songs():
    for i in range(3):
        result = d.search(type="release")
        tmp_song = SongDetails(title=result[i].title, year=result[i].year, country=result[i].country, styles= result[i].styles)
        """song = {
            "title": result.title,
            "release_year": result.year,
            "country": result.country,
            "duration": tag.duration,
            "styles": result.styles
        }"""
        song_list.append(tmp_song)

#endregion functions

#region main
collect_popular_songs()
print(song_list)

#endregion main