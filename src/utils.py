import os
from dotenv import load_dotenv
import spotipy
from notion_client import Client
from datetime import datetime

# Load environment variables
load_dotenv()

# Notion API setup
notion_token = os.environ.get('NOTION_SITEDB_TOKEN')
radio_history_db_id = os.environ.get('RADIO_HISTORY_DB_ID')
radio_suggestions_db_id = os.environ.get('RADIO_SUGGESTIONS_DB_ID')
notion = Client(auth=notion_token)

# Caching setup
cache = {
    "current_song": None,
    "recent_songs": None,
}
last_updated = {
    "current_song": datetime.min,
    "recent_songs": datetime.min,
}
CACHE_INTERVAL = 60  # seconds

def should_update(cache_key):
    return (datetime.now() - last_updated[cache_key]).total_seconds() > CACHE_INTERVAL

def get_current_song(token):
    if should_update("current_song"):
        try:
            spotify_obj = spotipy.Spotify(auth=token)
            current_track = spotify_obj.current_user_playing_track()
            if current_track and current_track['is_playing']:
                artist_name = current_track['item']['artists'][0]['name']
                track_name = current_track['item']['name']
                album_art_url = current_track['item']['album']['images'][0]['url']
                cache["current_song"] = {"artist": artist_name, "track": track_name, "album_art": album_art_url}
            else:
                cache["current_song"] = {"artist": "Not Playing", "track": "N/A", "album_art": "https://via.placeholder.com/150"}
            last_updated["current_song"] = datetime.now()
        except Exception as e:
            print(f"Error fetching current song from Spotify: {e}")
            cache["current_song"] =  {"artist": "Error", "track": "N/A", "album_art": "https://via.placeholder.com/150"}
            last_updated["current_song"] = datetime.now() #Still update the time, even if there is an error
    return cache["current_song"]

def get_recent_songs(token):
    if should_update("recent_songs"):
        try:
            spotify_obj = spotipy.Spotify(auth=token)
            recent_tracks_query = spotify_obj.current_user_recently_played(limit=50)
            recent_tracks = []
            for item in recent_tracks_query['items']:
                artist = item['track']['artists'][0]['name']
                track = item['track']['name']
                played_at = item['played_at']
                recent_tracks.append({"artist": artist, "track": track, "played_at": played_at})

            cache["recent_songs"] = recent_tracks
            last_updated["recent_songs"] = datetime.now()
        except Exception as e:
            print(f"Error fetching recent songs from Spotify: {e}")
            cache["recent_songs"] = []
            last_updated["recent_songs"] = datetime.now() #Still update even if there is an error
    return cache["recent_songs"]

def navbar():
    return """
    <nav>
        <ul>
            <li><a href="/">home</a></li>
            <li><a href="/about">about</a></li> 
            <li><a href="/cv">cv</a></li>
            <li><a href="/notes">notes</a></li>
            <li><a href="/radio">radio</a></li>
            <li><a href="/rir">reading list</a></li>
        </ul>
    </nav>
    """

def footer():
    return """
    <footer>
        <ul>
            <li><a href="mailto:pmchalvorsen@gmail.com">email</a></li>
            <li><a href="https://github.com/pmhalvor">github</a></li>
            <li><a href="https://www.linkedin.com/in/pmhalvor">linkedin</a></li>
        </ul>
    </footer>
    """
