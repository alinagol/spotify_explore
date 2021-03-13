import logging
import time

import requests
import utils

log = logging.getLogger(__name__)


class Spotify:
    """A wrapper for Spotify API."""

    SPOTIFY_API_URL = "https://api.spotify.com/v1"
    SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
    TIMEOUT = 600
    MAX_PAGES = 5
    MAX_RETRIES = 5

    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.expires_at = 0
        self.access_token = None
        self.session = self._create_session()

    def _get_access_token(self):
        log.info("Getting access token..")
        if self.access_token is None:
            with requests.Session() as session:
                r = session.post(
                    self.SPOTIFY_TOKEN_URL,
                    data={"grant_type": "client_credentials"},
                    auth=(self.client_id, self.client_secret),
                )
                if r.status_code == 200:
                    access_token = r.json()["access_token"]
                    self.access_token = access_token
                    self.expires_at = time.time() + r.json()["expires_in"]

    def _create_session(self):
        if self.access_token is None or (time.time() > self.expires_at - 60):
            self._get_access_token()
        headers = {
            "Authorization": f"Bearer {self.access_token}",
        }
        session = requests.Session()
        session.headers.update(headers)
        return session

    def _get(
        self, path: str = None, params: dict = None, url: str = None
    ) -> dict:
        request_url = url if url else f"{self.SPOTIFY_API_URL}/{path}"
        with self.session as s:
            n = 0
            while n < self.MAX_RETRIES:
                log.debug(n)
                response = s.get(request_url, params=params)
                try:
                    response.raise_for_status()
                except requests.exceptions.HTTPError as e:
                    if e.response.status_code == 401:
                        log.warning("Token expired.")
                        self._get_access_token()
                        n += 1
                        continue
                    elif e.response.status_code == 429:
                        sleep_time = int(response.headers["Retry-After"]) + 1
                        log.warning(
                            "Rate limit reached. Sleeping for %i.", sleep_time
                        )
                        time.sleep(sleep_time)
                        n += 1
                        continue
                    else:
                        log.warning(response.text)
                        raise
                break
            return response.json()

    def search(self, params: dict) -> dict:
        """Search by track title and artist name."""

        results = self._get(path="search", params=params)

        if results["tracks"]["items"]:
            log.debug("Found %i tracks", len(results["tracks"]["items"]))

            page = 0
            next_url = results["tracks"]["next"]

            while next_url and page < self.MAX_PAGES:
                log.debug("Searching next page...")
                try:
                    next_page = self._get(url=next_url)
                    results["tracks"]["items"].extend(
                        next_page["tracks"]["items"]
                    )
                    next_url = next_page["tracks"]["next"]
                    page += 1
                except requests.exceptions.RequestException:
                    break

            return results
        else:
            return {}

    def get_id(self, title: str, artist: str) -> str:
        """Get spotify id from track title and artist name."""
        params = {
            "type": "track",
            "q": f"track:{title} artist:{artist}",
            "limit": "50",
        }
        result = self.search(params)
        try:
            spotify_track_id = self.filter_found_tracks(
                result["tracks"]["items"], artist
            )["id"]
        except KeyError:
            log.debug(
                "Could not find %s. Retrying without artist name.", params["q"]
            )
            params_without_artist = {
                "type": "track",
                "q": f"track:{title}",
                "limit": "50",
            }
            result_without_artist = self.search(params_without_artist)
            try:
                spotify_track_without_artist = self.filter_found_tracks(
                    result_without_artist["tracks"]["items"], artist
                )
                spotify_track_id = spotify_track_without_artist["id"]
            except (KeyError, TypeError):
                log.warning("Could not find %s", params["q"])
                raise
        return spotify_track_id

    def get_features(self, spotify_id: str) -> dict:
        """Get spotify track details and audio features."""
        track_info = self._get(path=f"tracks/{spotify_id}")
        track_features = self._get(path=f"audio-features/{spotify_id}")
        track_info.update(track_features)
        return track_info

    @staticmethod
    def filter_found_tracks(tracks: list, artist: str) -> dict:
        """Filter tracks found in Spotify API.
        Returns the first track with matching artist name.
        """
        correct_track = dict()

        for track in tracks:
            track_artists = [
                utils.prepare_artist(x["name"].lower())
                for x in track["artists"]
            ]
            for track_artist in track_artists:
                if track_artist.find(artist) != -1:
                    correct_track = track
                    break
            else:
                continue
            break

        if not correct_track:
            log.debug("Could not match '%s' in found tracks.", artist)
        return correct_track
