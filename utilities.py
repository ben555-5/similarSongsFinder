import re

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