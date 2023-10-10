import re
import glob
import base64
from urllib.parse import quote
from pathlib import Path


import requests
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC
import typer


def has_artwork(mp3_path: str):
    """Check if MP3 already has embedded artwork."""
    audio = MP3(mp3_path, ID3=ID3)
    return any(key.startswith("APIC") for key in audio.tags.keys())


def match_song(local: tuple[str, str], remote: tuple[str, str]):
    remote_artist, remote_title = remote
    remote_artist = remote_artist.strip().lower().replace(" &", ",")
    remote_title = re.split(r"([\-,\[\(]|feat)", remote_title.strip().lower(), 1)[0]
    local_artist, local_title = local
    local_artist = local_artist.strip().lower().replace(" &", ",")
    local_title = re.split(r"[\-,\[\(]", remote_title.strip().lower(), 1)[0]

    return (
        local_artist.strip() == remote_artist.strip()
        and local_title.strip() == remote_title.strip()
    )


def show_image_in_iterm2(url: str):
    try:
        resp = requests.get(url)
        resp.raise_for_status()
    except Exception as err:
        print(err)
        return
    img_data = resp.content
    b64_data = base64.b64encode(img_data).decode("utf-8")
    width = "25"
    height = "auto"
    print(
        f"\033]1337;File=inline=1;width={width};height={height};preserveAspectRatio=1:{b64_data}\a"
    )


def search_itunes_artwork(artist: str, title: str, no_input: bool = False):
    """Search iTunes for album artwork."""
    title = title.split("(", 1)[0]
    query_parts = artist, title
    query = " ".join([p for p in query_parts if p])
    url = f"https://itunes.apple.com/search?term={quote(query)}&entity=song&limit=5"

    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()
    results = data.get("results", [])

    if len(results) == 0:
        return None

    if len(results) == 1:
        artwork_url = results[0]["artworkUrl100"]
        return artwork_url.replace("100x100", "1000x1000")  # Get larger image

    for result in results:
        if match_song(
            (result["artistName"], result["collectionCensoredName"]),
            (artist, title),
        ):
            artwork_url = result["artworkUrl100"]
            return artwork_url.replace("100x100", "1000x1000")

    if no_input:
        return

    print(f"Candidates for '{artist}' - '{title}':")
    for i, result in enumerate(results[:3]):
        print(f"{i + 1} - {result['artistName']} - {result['collectionCensoredName']}")
        show_image_in_iterm2(result["artworkUrl100"])

    while True:
        idx = input("Index? (0 to skip) ")
        idx = idx.strip()
        try:
            i = int(idx)
        except ValueError:
            continue
        if i == 0:
            break
        try:
            artwork_url = results[i - 1]["artworkUrl100"]
            return artwork_url.replace("100x100", "1000x1000")
        except IndexError:
            continue

    return None


def set_mp3_artwork(mp3_path: Path, image_url: str):
    """Download and set artwork in an MP3 file."""
    audio = MP3(str(mp3_path), ID3=ID3)
    try:
        audio.add_tags()
    except Exception as err:
        print(err)
        pass
    audio.tags.delall("APIC")
    img_data = requests.get(image_url).content
    audio.tags.add(
        APIC(encoding=3, mime="image/jpeg", type=3, desc="Cover", data=img_data)
    )
    audio.save()
    print(f"✅ Artwork set for {mp3_path}")


def complete_path(incomplete):
    print(incomplete)
    return incomplete


def main(files: list[Path], overwrite: bool = False, no_input: bool = False):
    actual_files = []
    for path in files:
        if path.is_dir():
            for f in glob.glob(str(path / "*.mp3")):
                actual_files.append(Path(f))
        elif path.name.endswith(".mp3"):
            actual_files.append(path)

    for file in actual_files:
        if not overwrite and has_artwork(file):
            print(f"   Skipped — {file.name} already has artwork.")
            continue

        audio = MP3(str(file), ID3=ID3)
        artist = str(audio.tags.get("TPE1") or "").strip()
        title = str(audio.tags.get("TIT2") or "").strip()
        if not artist or not title:
            print(f"   ❌ {file.name} Missing metadata.")
            continue

        print(f"   🔍 Searching artwork for: {artist} - {title}")
        try:
            image_url = search_itunes_artwork(artist, title, no_input)
        except Exception as err:
            print(err)
            continue

        if image_url:
            set_mp3_artwork(file, image_url)
        else:
            print("   ⚠️ No match.")


if __name__ == "__main__":
    typer.run(main)
