import pytest
from src.spotify import parse_track, parse_episode

@pytest.fixture
def sample_track():
    return {
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
                "images": [
                    {
                        "height": 640,
                        "url": "https://i.scdn.co/image/ab67616d0000b273ec70f68a0cc8b408e194aa97",
                        "width": 640
                    }
                ],
                "name": "Harmonious Visit",
                "release_date": "2025-01-24",
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
            "duration_ms": 155500,
            "external_urls": {
                "spotify": "https://open.spotify.com/track/0eS7dmrKdI0oy1rAR1k8Y5"
            },
            "id": "0eS7dmrKdI0oy1rAR1k8Y5",
            "name": "Harmonious Visit",
            "popularity": 44,
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

@pytest.fixture
def sample_episode():
    return {
        "timestamp": 1741380635516,
        "context": None,
        "progress_ms": 3372619,
        "item": None,
        "currently_playing_type": "episode",
        "actions": {
            "disallows": {
                "pausing": True
            }
        },
        "is_playing": False
    }

def test_parse_track(sample_track):
    # Assemble
    expected_result = {
        "lead_artist": "Sheila's Disciples",
        "artist": "Sheila's Disciples",
        "track": "Harmonious Visit",
        "album_art": "https://i.scdn.co/image/ab67616d0000b273ec70f68a0cc8b408e194aa97",
        "played_at": "2025-03-07T18:25:48.987Z",
        "duration": 155500,
        "popularity": 44,
        "progress": 0,
        "uri": "spotify:track:0eS7dmrKdI0oy1rAR1k8Y5",
        "url": "https://open.spotify.com/track/0eS7dmrKdI0oy1rAR1k8Y5"
    }

    # Act
    result = parse_track(sample_track)

    # Assert
    assert result == expected_result

def test_parse_episode(sample_episode):
    # Assemble
    expected_result = {
        "artist": "",
        "track": "Playing a podcast",
        "album_art": "local/static/img/podcast.png",
        "played_at": "",
        "progress": 0
    }

    # Act
    result = parse_episode(sample_episode)

    # Assert
    assert result == expected_result