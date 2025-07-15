import re
from pymongo import MongoClient
from datetime import datetime

client = MongoClient("mongodb://localhost:27017/")
db = client["Spotify_Lyrics"]
collection = db["Lyrics_data"]

folder = "./lyrics_data"

def parse_lyrics_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex to split on the song header lines (case insensitive)
    # Example header: lyrics for 'cardigan' by Taylor Swift:
    pattern = re.compile(r"lyrics for '(.+?)' by (.+?):", re.IGNORECASE)
    matches = list(pattern.finditer(content))

    for i, match in enumerate(matches):
        title = match.group(1).strip().title()
        artist = match.group(2).strip().title()
        start = match.end()

        # Determine end of this song lyrics block
        if i + 1 < len(matches):
            end = matches[i + 1].start()
        else:
            end = len(content)

        # Extract lyrics block between current header and next header
        lyrics_block = content[start:end].strip()

        # Optional: remove extra metadata lines before actual lyrics
        # For example, remove first 5 lines if they are metadata (customize as needed)
        lines = lyrics_block.split('\n')
        # Heuristic: skip first N lines if they don't look like lyrics (adjust N as needed)
        N = 5
        lyrics = '\n'.join(lines[N:]).strip()

        doc = {
            "title": title,
            "artist": artist,
            "lyrics": lyrics,
            "retrieved_at": datetime.utcnow(),
            "status": "success",
            "error": None
        }

        collection.insert_one(doc)
        print(f"Inserted: {title} by {artist}")

# Run for all files in folder
import os
for filename in os.listdir(folder):
    if filename.endswith(".txt"):
        filepath = os.path.join(folder, filename)
        print(f"Parsing file: {filename}")
        parse_lyrics_file(filepath)



