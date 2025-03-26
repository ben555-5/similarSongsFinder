import discogs_client

def fetchTrendingSongs():
    d = discogs_client.Client('ExampleApplication/0.1', user_token="SRhITdROZteKwXDfenFQwentXgLxUyjvBbTvWpVN")
    tmp_release = d.search(type='release', sort='hot,desc')
    LIMIT = 1000
    counter = 0
    for i in tmp_release:
        print(i)
        if counter >= LIMIT:
            break
        counter += 1
    print(counter)



