import discogs_client
import re

token = "GVOasQPZopgGnCjiQpCQlsbIsvocZxzMkEsJNURq"

d = discogs_client.Client('ExampleApplication/0.1', user_token=token)


def clean_string(s: str) -> str:
    # Convert to lowercase
    s = s.lower()

    # Remove quotes
    s = re.sub(r'[\'\u2019"]', '', s)
    
    # Remove everything inside parentheses (including the parentheses themselves)
    s = re.sub(r'\(.*?\)', '', s)
    
    # Replace any sequence of separators (non-word characters) with a single underscore
    s = re.sub(r'[^\w]+', '_', s)
    
    # Remove leading and trailing underscores
    s = s.strip('_')
    
    return s

results = d.search(type="release", sort="hot")
budget = 20
mapping = {}
for result in results:
    for track in result.tracklist:
        normalized_title = clean_string(track.title)
        print(f"{track.title} => {normalized_title}")
        l = mapping.get(normalized_title, [])
        l.append(track.title)
        mapping[normalized_title] = l


    budget-=1
    if budget == 0:
        break

import json
print(json.dumps(mapping, indent=2))

    
    
