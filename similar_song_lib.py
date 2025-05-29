from database import *
from best_results_cache_class import BestResultCache
from utilities import clean_string

def calculate_score(song1, song2):
    score = 0

    # מדינה זהה
    if song1.country == song2.country:
        score += 5

    # קרבה בשנים
    try:
        year_diff = abs(song1.year - song2.year)
        if year_diff == 0:
            score += 5
        elif year_diff <= 2:
            score += 4
        elif year_diff <= 5:
            score += 3
        elif year_diff <= 10:
            score += 1
    except:
        pass

    # סגנונות משותפים
    try:
        styles1 = set(map(str.lower, song1.styles)) if song1.styles else set()
        styles2 = set(map(str.lower, song2.styles)) if song2.styles else set()
        shared = styles1 & styles2
        score += len(shared) * 2
    except:
        pass

    # שם שיר כלול בשם השני
    try:
        if clean_string(song2.title) in clean_string(song1.title):
            score += 1
    except:
        pass

    return score

def get_best_matches(song_id):
    user_song = get_song_by_id(song_id)
    song_list = get_all_songs([song_id])
    cache = BestResultCache(max_size=10)

    for song in song_list:
        cache.update_result(song, calculate_score(user_song, song))

    results = cache.get_best_results()
    print("the result of get best matches is: ", results)
    return results





