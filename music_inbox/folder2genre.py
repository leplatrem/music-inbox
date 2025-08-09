import logging
import os
from pathlib import Path

import eyed3
import typer

app = typer.Typer()


@app.command()
def main(path: Path):
    """
    Set the `Genre` tag on files recursively from PATH.

    Containing folder name is used as genre.
    """
    logging.getLogger("eyed3").setLevel(logging.ERROR)

    audios = []
    for root, dirs, files in os.walk(str(path)):
        leaf = os.path.basename(root)
        if leaf.startswith("_"):
            continue
        for f in files:
            _, ext = os.path.splitext(f)
            if ext not in (".mp3",):
                continue
            audios.append((leaf, os.path.join(root, f)))

    for genre, f in audios:
        audiofile = eyed3.load(f)
        try:
            if audiofile.tag.genre != genre:
                print(genre, f)
                audiofile.tag.genre = genre
                audiofile.tag.save()
        except Exception as e:
            print(f, e)


if __name__ == "__main__":
    app()
