import os
import glob
import re
import sys
import time
from pathlib import Path

import eyed3
import typer


def main(files: list[Path]):
    actual_files = []
    for path in files:
        if path.is_dir():
            for f in glob.glob(str(path / "*.mp3")):
                actual_files.append(Path(f))
        elif path.name.endswith(".mp3"):
            actual_files.append(path)

    renames = []
    errors = []
    for file in actual_files:
        f = str(file)
        folder = os.path.dirname(f)
        basename = os.path.basename(f)
        filename, ext = os.path.splitext(basename)

        # This prevents some ID3 errors?!
        time.sleep(0.5)
        audiofile = eyed3.load(f)
        if audiofile is None:
            raise ValueError(f"{f} has no info")

        if audiofile.tag.encoded_by == "Beatport" or audiofile.tag.artist not in (
            "",
            None,
        ):
            artist = re.sub(r"\s?[/&]\s?", ", ", audiofile.tag.artist)
            title = audiofile.tag.title or ""
            newfilename = artist + " - " + title + ext
            newfilename = re.sub(r'\s?[\'<>:"/\\|?*\]\[]\s?', " ", newfilename)
            if basename != newfilename:
                renames.append((folder, basename, newfilename))

        else:
            nobrackets = re.sub(r"\s?\[([^\]]+)\]?", "", filename)
            if nobrackets != filename:
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

            dirty = False
            if not audiofile.tag.artist or (artist and audiofile.tag.artist != artist):
                audiofile.tag.artist = artist
                dirty = True
            if not audiofile.tag.title or (title and audiofile.tag.title != title):
                audiofile.tag.title = title
                dirty = True
            if dirty:
                print("Save", artist, "-", title, f"(Genre: {audiofile.tag.genre})")
                audiofile.tag.save()

    if errors:
        print("\n".join(errors))
        sys.exit(1)

    if renames:
        print("\n - ".join(f"{s}\n   {d}" for _, s, d in renames))
        answer = ""
        while answer.lower() not in ("y", "n"):
            answer = input("Proceed? Y/n ")
            if answer.lower() == "n":
                sys.exit(0)

    for folder, s, d in renames:
        os.rename(os.path.join(folder, s), os.path.join(folder, d))


if __name__ == "__main__":
    typer.run(main)
