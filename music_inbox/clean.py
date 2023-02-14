import os
import glob
import re
import sys

import eyed3


def main():
    files = glob.glob(sys.argv[1])
    errors = []
    for f in files:
        print(f)
        folder = os.path.dirname(f)
        basename = os.path.basename(f)
        filename, ext = os.path.splitext(basename)
        audiofile = eyed3.load(f)

        if audiofile.tag.encoded_by == "Beatport":
            artist = audiofile.tag.artist
            title = audiofile.tag.title
            filename = artist + " - " + title + ".mp3"
            os.rename(f, os.path.join(folder, filename))
        else:
            nobrackets = re.sub("\\[+.\\]+", "", filename)
            os.rename(f, nobrackets)

            artist, title = nobrackets.rsplit(" - ", 1)

            if audiofile is None:
                raise ValueError(f"{f} has no info")

            _, bitrate = audiofile.info.bit_rate
            if bitrate < 320:
                print(f"⚠️  {f} has low bitrate {bitrate}")
            if bitrate < 192:
                errors.append(f"{f} has bitrate {bitrate}")
                continue

            audiofile.tag.artist = artist
            audiofile.tag.title = title
            print("Save", artist, "-", title, audiofile.tag.genre)
            audiofile.tag.save()

    print("\n".join(errors))
