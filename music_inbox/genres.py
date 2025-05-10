import asyncio
import glob
import json
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
        soup = BeautifulSoup(html, features="html.parser")
        page_data = json.loads(soup.select("script#__NEXT_DATA__")[0].string)
        
        queries_results = [
            q["state"]["data"]["tracks"]["data"]
            for q in page_data["props"]["pageProps"]["dehydratedState"]["queries"]
        ]
        songs_genres = []
        for song in queries_results[0][:5]:
            artists = [a["artist_name"] for a in song["artists"]]
            title = song["track_name"]
            genres = [g["genre_name"] for g in song["genre"]]
            songs_genres.append((", ".join(artists), title, tuple(genres)))
        return songs_genres


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

        print(f)
        audiofile = eyed3.load(f)
        if audiofile.tag and audiofile.tag.artist:
            song = (audiofile.tag.artist.strip(), audiofile.tag.title.strip())
        else:
            song = filename.rsplit("-", 1)
        # songs.append(song)

    asyncio.run(search_all(songs))
