import os
from random import shuffle
from collections import Counter
import spotipy
from spotipy.oauth2 import SpotifyOAuth

from secrets import SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI

os.environ["SPOTIPY_CLIENT_ID"] = SPOTIPY_CLIENT_ID
os.environ["SPOTIPY_CLIENT_SECRET"] = SPOTIPY_CLIENT_SECRET
os.environ["SPOTIPY_REDIRECT_URI"] = SPOTIPY_REDIRECT_URI


class SpotifyApiHandler:

    def __init__(self) -> None:
        super().__init__()

        scope = "user-library-read"
        self.sp = spotipy.Spotify(auth_manager = SpotifyOAuth(cache_path = ".cache", scope = scope))

        first_results = self.sp.current_user_saved_tracks(limit = 1, offset = 0)
        self.num_favourites = first_results["total"]

    @staticmethod
    def print_song(song: dict):
        print(song["artists"][0]["name"], "-", song["name"])

    def get_random_tracks(self, exclude_hungarian_songs = False, limit = 1):

        indices = list(range(self.num_favourites))
        shuffle(indices)

        i = 0
        songs = []
        while i < self.num_favourites:
            results = self.sp.current_user_saved_tracks(limit = 1, offset = indices[i])
            main_artist = results['items'][0]["track"]["artists"][0]["name"]
            track_name = results['items'][0]["track"]["name"]
            if not exclude_hungarian_songs or not self.is_hungarian(main_artist, track_name):
                songs.append(results['items'][0]["track"])

            if len(songs) == limit:
                break

            i += 1

        return songs

    # todo find an api to determine nationality
    @staticmethod
    def is_hungarian(main_artist, track_name):
        hungarian_characters_and_phrases = ["é", "á", "ó", "ö", "ő", "ú", "ü", "ű", "í", "Bëlga"]

        if "Beyoncé" in main_artist:  # we love Beyoncé
            return False

        for char in hungarian_characters_and_phrases:
            if char in main_artist or char in track_name:
                return True

        return False

    def get_recommendation_for_single_song(self, song_id, limit = 1):
        return self.sp.recommendations(seed_tracks = [song_id], limit = limit, country = "HU")["tracks"]

    def get_random_recommendation(self, limit = 10):
        songs = self.get_random_tracks(exclude_hungarian_songs = True, limit = 5)

        ids = [s["id"] for s in songs]

        recommendations = self.sp.recommendations(seed_tracks = ids, limit = limit)["tracks"]
        return recommendations


if __name__ == '__main__':
    spotiapi = SpotifyApiHandler()

    # song = spotiapi.get_random_tracks(True, 5)
    # for s in song:
    #     spotiapi.print_song(s)

    acc = []
    for i in range(200):
        songs = spotiapi.get_random_recommendation(20)
        acc.extend([song["name"] for song in songs])
    counted = Counter(acc)
    counted = sorted(counted.items(), key=lambda item: -item[1])
    for c in counted:
        print(c)
    # for s in counted[:10]:
    #     spotiapi.print_song(s)
    # print("#####################")