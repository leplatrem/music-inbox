import json
import sys

from pyrekordbox import MasterDatabase

db = MasterDatabase()

tracks = []

for content in db.get_content():
    track = {
        "id": content.ID,
        "artist": content.Artist.Name,
        "title": content.Title,
        "rating": content.Rating,
        "bpm": content.BPM,
        "key": content.Key.ScaleName if content.Key else None,
        "bitrate": content.BitRate,
        "length": content.Length,
        "color": content.Color.Commnt if content.Color else None,
        "tags": [
            t for t in content.MyTagNames
        ],
        "genre": content.Genre.Name if content.Genre else None,
        "path": content.FolderPath,

    }
    tracks.append(track)

json.dump(tracks, sys.stdout, indent=4)
