import discogs_client
d = discogs_client.Client('ExampleApplication/0.1', user_token="GVOasQPZopgGnCjiQpCQlsbIsvocZxzMkEsJNURq")


def search_song_by_title(track_title):
    result = d.search(type="release", q=track_title)
    if len(result) == 0:
        return None
    return result[0]

