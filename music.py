import spotipy 
import webbrowser
import mysecrets as sc
from spotipy.oauth2 import SpotifyClientCredentials

class SpotifyWrapper:
##
    def __init__(self) -> None:
        self.sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=sc.spotify_clientID, client_secret=sc.spotify_clientSecret,))
         
    def playSong(self, searchPhrase : str):
        try:
            results = self.sp.search(q=searchPhrase, limit=20)
            songs_dict = results['tracks'] 
            song_items = songs_dict['items'] 
            song = song_items[0]['external_urls']['spotify'] 
            webbrowser.open(song)
            return "found"
        except:
            return "failed"


if __name__ == "__main__":
    player = SpotifyWrapper()
    player.playSong("brother louie")