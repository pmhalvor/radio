import spotipy
import datetime as dt 
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)

# Load environment variables
load_dotenv()


def parse_track(track):
    _ = {     # track_format
        "track": {
            "album": {
                "album_type": "single",
                "artists": [
                    {
                        "external_urls": {
                            "spotify": "https://open.spotify.com/artist/6fVRZUOhSnwc3dtmooHbkO"
                        },
                        "href": "https://api.spotify.com/v1/artists/6fVRZUOhSnwc3dtmooHbkO",
                        "id": "6fVRZUOhSnwc3dtmooHbkO",
                        "name": "Sheila's Disciples",
                        "type": "artist",
                        "uri": "spotify:artist:6fVRZUOhSnwc3dtmooHbkO"
                    }
                ],
                "available_markets": [
                    "NO",
                    "..."
                ],
                "external_urls": {
                    "spotify": "https://open.spotify.com/album/5dQEk7k0aOuoCN119pP2sH"
                },
                "href": "https://api.spotify.com/v1/albums/5dQEk7k0aOuoCN119pP2sH",
                "id": "5dQEk7k0aOuoCN119pP2sH",
                "images": [
                    {
                        "height": 640,
                        "url": "https://i.scdn.co/image/ab67616d0000b273ec70f68a0cc8b408e194aa97",
                        "width": 640
                    },
                    {
                        "height": 300,
                        "url": "https://i.scdn.co/image/ab67616d00001e02ec70f68a0cc8b408e194aa97",
                        "width": 300
                    },
                    {
                        "height": 64,
                        "url": "https://i.scdn.co/image/ab67616d00004851ec70f68a0cc8b408e194aa97",
                        "width": 64
                    }
                ],
                "name": "Harmonious Visit",
                "release_date": "2025-01-24",
                "release_date_precision": "day",
                "total_tracks": 1,
                "type": "album",
                "uri": "spotify:album:5dQEk7k0aOuoCN119pP2sH"
            },
            "artists": [
                {
                    "external_urls": {
                        "spotify": "https://open.spotify.com/artist/6fVRZUOhSnwc3dtmooHbkO"
                    },
                    "href": "https://api.spotify.com/v1/artists/6fVRZUOhSnwc3dtmooHbkO",
                    "id": "6fVRZUOhSnwc3dtmooHbkO",
                    "name": "Sheila's Disciples",
                    "type": "artist",
                    "uri": "spotify:artist:6fVRZUOhSnwc3dtmooHbkO"
                }
            ],
            "available_markets": [
                "NO",
                "..."
            ],
            "disc_number": 1,
            "duration_ms": 155500,
            "explicit": False,
            "external_ids": {
                "isrc": "SEXGF2397794"
            },
            "external_urls": {
                "spotify": "https://open.spotify.com/track/0eS7dmrKdI0oy1rAR1k8Y5"
            },
            "href": "https://api.spotify.com/v1/tracks/0eS7dmrKdI0oy1rAR1k8Y5",
            "id": "0eS7dmrKdI0oy1rAR1k8Y5",
            "is_local": False,
            "name": "Harmonious Visit",
            "popularity": 44,
            "preview_url": "https://p.scdn.co/mp3-preview/24529a5e588cee5c8a9b4eed583518c16e52ed9d?cid=9656ff22d7604d078e98e54a1870b92d",
            "track_number": 1,
            "type": "track",
            "uri": "spotify:track:0eS7dmrKdI0oy1rAR1k8Y5"
        },
        "played_at": "2025-03-07T18:25:48.987Z",
        "context": {
            "href": "https://api.spotify.com/v1/playlists/37i9dQZF1DX1n9whBbBKoL",
            "external_urls": {
                "spotify": "https://open.spotify.com/playlist/37i9dQZF1DX1n9whBbBKoL"
            },
            "type": "playlist",
            "uri": "spotify:playlist:37i9dQZF1DX1n9whBbBKoL"
        }
    }
    if track.get('track') is None:
        # currently playing sends tracks under 'item' key
        track['track'] = track['item']  

    lead_artist = track['track']['artists'][0]['name']
    artists = ', '.join([artist['name'] for artist in track['track']['artists']])
    track_name = track['track']['name']
    album_art_url = track['track']['album']['images'][0]['url']
    duration = track['track']['duration_ms']
    played_at = (
        track['played_at'] 
        if track.get('played_at', False) 
        else 
        # currently playing relies on (start) timestamp for played_at
        dt.datetime.utcfromtimestamp(track['timestamp']  / 1000).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    )
    popularity = track['track']['popularity']
    progress = track.get('progress_ms', 0)
    url = track['track']['external_urls']['spotify']
    uri = track['track']['uri']
    
    return {
        "lead_artist": lead_artist,
        "artist": artists,
        "track": track_name,
        "album_art": album_art_url,
        "played_at": played_at,
        "duration": duration,
        "popularity": popularity,
        "progress": progress,
        "uri": uri,
        "url": url,
    }


def parse_episode(episode):
    """
    response format when podcast is playing:
    {
        "timestamp": 1741380635516,
        "context": null,
        "progress_ms": 3372619,
        "item": null,
        "currently_playing_type": "episode",
        "actions": {
            "disallows": {
                "pausing": true
            }
        },
        "is_playing": False
    }
    """
    return {
        "artist": "",
        "track": "Playing a podcast",
        "album_art": "local/static/img/podcast.png",
        "played_at": "",
        "progress": 0
    }


def get_current_song(token):
    spotify_obj = spotipy.Spotify(auth=token)
    current_track = spotify_obj.current_user_playing_track()

    if current_track is not None:
        logging.info(", ".join(current_track.keys()))
    else:
        logging.info("No current track playing.")

    if current_track is None:
        return {
            "artist": "",
            "track": "not playing",
            "album_art": "local/static/img/empty_album.png",
            "played_at": "",
            "progress": 0
        }

    elif current_track.get("currently_playing_type") == "track":
        return parse_track(current_track)

    elif current_track.get("currently_playing_type") == "episode":
        return parse_episode(current_track)
    
    else:
        return {
            "artist": "",
            "track": "Unknown rtack type",
            "album_art": "local/static/img/empty_album.png",
            "played_at": "",
            "progress": 0
        }


def get_recent_songs(token):
    spotify_obj = spotipy.Spotify(auth=token)
    recent_tracks_query = spotify_obj.current_user_recently_played(limit=50)
    recent_tracks = []

    for i, item in enumerate(recent_tracks_query['items']):
        parsed_track = parse_track(item)
        # print(json.dumps(parsed_track, indent=4))
        recent_tracks.append(parsed_track)


    return recent_tracks


def get_tracks(token=None, batch_id_str=None) -> dict:
    spotify_obj = spotipy.Spotify(auth=token)
    tracks = spotify_obj.tracks(batch_id_str.split(','))
    return tracks.get('tracks', {})


if __name__ == '__main__':
    pass