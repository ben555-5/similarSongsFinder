from database import *
from best_results_cache_class import BestResultCache


def calculate_score(song1, song2):
    score = 0
    if song1.country == song2.country:
        score += 5
    return score
def get_best_matches(song_id):
    user_song = get_song_by_id(song_id)
    song_list = get_all_songs([song_id])
    cache = BestResultCache(max_size=10)
    for song in song_list:
        cache.update_result(song,calculate_score(user_song, song))
    results = cache.get_best_results()
    print("the result of get best matches is: ", results)
    return results






