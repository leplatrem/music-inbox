import logging
import os
import sys

import eyed3


def main():
    rootdir = sys.argv[1]
    
    logging.getLogger("eyed3").setLevel(logging.ERROR)

    audios = []
    for root, dirs, files in os.walk(rootdir):
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
