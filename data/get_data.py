import logging
import os

import pymongo
import requests
import utils
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
from spotify_client import Spotify

log = logging.getLogger(__name__)

WIKI_URL = (
    "https://en.wikipedia.org/wiki/Billboard_Year-End_Hot_100_singles_of_"
)

mongo_uri = f'mongodb://{os.getenv("MONGODB_USERNAME")}:{os.getenv("MONGODB_PASSWORD")}@{os.getenv("MONGODB_HOSTNAME")}:27017'
with pymongo.MongoClient(mongo_uri) as client:
    db_tracks = client[os.getenv("MONGODB_DATABASE")]["tracks"]
    db_tracks_no_id = client[os.getenv("MONGODB_DATABASE")]["tracks_no_id"]

spotify = Spotify(
    os.getenv("SPOTIFY_CLIENT_ID"), os.getenv("SPOTIFY_CLIENT_SECRET")
)


def get_top_charts():
    log.info("Getting top charts from Wiki.")
    for year in range(1940, 2021):
        url = f"{WIKI_URL}_{year}"
        page = requests.get(url)
        if page.status_code == 200:
            soup = BeautifulSoup(page.text, "html.parser")
            chart = soup.find("table", {"class": "wikitable sortable"})
            for row in chart.findAll("tr")[1:]:
                line = row.get_text().split("\n")
                line = [item.strip().strip('"') for item in line if item]
                try:
                    track = {
                        "position": line[0],
                        "title": line[1],
                        "artist": line[2],
                        "year": year,
                    }
                except IndexError:
                    continue
                try:
                    spotify_id = get_spotify_id(
                        track["title"], track["artist"]
                    )
                    track.update(spotify.get_features(spotify_id))
                    db_tracks.insert_one(track)
                except (RequestException, KeyError, TypeError) as ex:
                    log.warning(ex)
                    db_tracks_no_id.insert_one(track)


def get_spotify_id(title: str, artist: str) -> str:
    title = utils.prepare_title(title)
    artist = utils.prepare_artist(artist)
    spotify_id = spotify.get_id(title, artist)
    return spotify_id


def main():
    get_top_charts()


if __name__ == "__main__":
    main()
