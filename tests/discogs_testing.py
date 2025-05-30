from discogs_library import search_song_by_title


def test1():
    result = search_song_by_title("shape of you - ed sheeran")
    if "Release" == result.__class__.__name__:
        print("passed")
    else:
        print("failed")

def test2():
    result = search_song_by_title("SNOOP DOGG - Conflicted feat. NAS")
    if result is None:
        print("passed")
    else:
        print("failed")
test1()
test2()
