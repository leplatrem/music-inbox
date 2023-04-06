import os
import glob
import re
import sys

import eyed3


def main():
    renames = []
    errors = []
    files = glob.glob(sys.argv[1])
    for f in files:
        folder = os.path.dirname(f)
        basename = os.path.basename(f)
        filename, ext = os.path.splitext(basename)

        audiofile = eyed3.load(f)
        if audiofile is None:
            raise ValueError(f"{f} has no info")

        if audiofile.tag.encoded_by == "Beatport":
            artist = audiofile.tag.artist
            title = audiofile.tag.title
            newfilename = artist + " - " + title + ext
            renames.append((folder, basename, newfilename))

        else:
            nobrackets = re.sub("\s+?\[([^\]]+)\]?", "", filename)
            renames.append((folder, basename, nobrackets + ext))

            try:
                artist, title = nobrackets.rsplit(" - ", 1)
            except ValueError as exc:
                raise ValueError(f"Filename has bad format: {f}") from exc

            _, bitrate = audiofile.info.bit_rate
            if bitrate < 320:
                print(f"⚠️  {f} has low bitrate {bitrate}")
            if bitrate < 192:
                errors.append(f"{f} has bitrate {bitrate}")
                continue

            audiofile.tag.artist = artist.strip()
            audiofile.tag.title = title.strip()
            print("Save", artist, "-", title, f"(Genre: {audiofile.tag.genre})")
            audiofile.tag.save()

    if errors:
        print("\n".join(errors))
        sys.exit(1)

    print("\n - ".join(f"{s}\n   {d}" for _, s, d in renames))
    answer = ""
    while answer.lower() not in ("y", "n"):
        answer = input("Proceed? Y/n")
        if answer.lower() == "n":
            sys.exit(0)

    for folder, s, d in renames:
        os.rename(os.path.join(folder, s), os.path.join(folder, d))
