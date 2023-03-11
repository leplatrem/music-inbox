import asyncio
import glob
import re
import os
import sys

import aiohttp
import eyed3
from bs4 import BeautifulSoup


class Beatport:
    @property
    def name(self):
        return self.__class__.__name__

    async def fetch(self, session, keywords):
        encoded = keywords.replace(" ", "+")
        print(f"Search for {encoded}")
        url = f"https://www.beatport.com/search?q={encoded}"
        async with session.get(url) as response:
            return await response.text()

    async def search(self, session, keywords):
        html = await self.fetch(session, keywords)
        print("Fetch page for", keywords)
        soup = BeautifulSoup(html, "html.parser")
        songs = soup.select(".bucket.tracks .buk-track-meta-parent")
        songs_genres = []
        for song in songs:
            artists_links = song.select("p.buk-track-artists a")
            artists = [link.string.strip() for link in artists_links]
            title_span = song.select("span.buk-track-primary-title")
            title = title_span[0].string.strip()
            genre_links = song.select("p.buk-track-genre a")
            genres = set(link.string for link in genre_links)
            songs_genres.append((", ".join(artists), title, tuple(genres)))
        return set(songs_genres)


async def search(session, keywords):
    providers = [Beatport()]
    futures = [provider.search(session, keywords) for provider in providers]
    results = await asyncio.gather(*futures)
    return list(zip(providers, results))


async def search_all(songs):
    async with aiohttp.ClientSession() as session:
        futures = [search(session, f"{artist} {title}") for (artist, title) in songs]
        results = await asyncio.gather(*futures)

    for (artist, title), results in zip(songs, results):
        print(f" - {artist} - {title}")
        for result in results:
            provider, found_songs = result
            match = [
                (a, t, g) for (a, t, g) in found_songs if artist == a and title == t
            ]
            if len(match) == 1:
                found_songs = match
            print(f"   {provider.name}")
            for bt_artists, bt_title, genres in found_songs:
                genres = ", ".join(genres)
                print(f"    - {bt_artists} - {bt_title}: \033[1m{genres}\033[0m")


def main():
    songs = []
    for f in glob.glob(sys.argv[1]):
        folder = os.path.dirname(f)
        basename = os.path.basename(f)
        filename, ext = os.path.splitext(basename)

        audiofile = eyed3.load(f)
        if audiofile.tag and audiofile.tag.artist:
            song = (audiofile.tag.artist.strip(), audiofile.tag.title.strip())
        else:
            song = filename.rsplit("-", 1)
        songs.append(song)

    asyncio.run(search_all(songs))
