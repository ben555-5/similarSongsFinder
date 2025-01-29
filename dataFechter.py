from ytmusicapi import YTMusic
import json
#YTMusic.search(query: str, filter: str | None = None, scope: str | None = None, limit: int = 20, ignore_spelling: bool = False) → list[dict]

yt = YTMusic()

res = yt.search(query="Dua Lipa", filter="songs", limit=1)

print(json.dumps(res, indent=2))