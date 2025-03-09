import pytest
from unittest.mock import patch
from new_radio.app import app
from new_radio.worker import get_current_song, get_recent_songs
from new_radio.worker.authorize import get_token
from datetime import datetime, timedelta

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_get_current_song_playing(client):
    mock_response = {
        'is_playing': True,
        'item': {
            'artists': [{'name': 'Test Artist'}],
            'name': 'Test Track',
            'album': {'images': [{'url': 'test_url'}]}
        }
    }
    with patch('new_radio.utils.spotipy.Spotify.current_user_playing_track', return_value=mock_response) as mock_spotify:
        result = get_current_song("test_token")
        assert result == {"artist": "Test Artist", "track": "Test Track", "album_art": "test_url"}

def test_get_current_song_not_playing(client):
    mock_response = {'is_playing': False}
    with patch('new_radio.utils.spotipy.Spotify.current_user_playing_track', return_value=mock_response) as mock_spotify:
        result = get_current_song("test_token")
        assert result == {"artist": "Not Playing", "track": "N/A", "album_art": "https://via.placeholder.com/150"}

def test_get_current_song_error(client):
    with patch('new_radio.utils.spotipy.Spotify.current_user_playing_track', side_effect=Exception("Test Error")) as mock_spotify:
        result = get_current_song("test_token")
        assert result == {"artist": "Error", "track": "N/A", "album_art": "https://via.placeholder.com/150"}

def test_get_recent_songs(client):
    mock_response = {
        "items": [
            {
                "track": {
                    "artists": [{"name": "Artist 1"}],
                    "name": "Track 1",
                },
                "played_at": "2024-03-01T10:00:00"
            },
            {
                "track": {
                    "artists": [{"name": "Artist 2"}],
                    "name": "Track 2",
                },
                "played_at": "2024-03-01T09:00:00"
            }
        ]
    }
    with patch('new_radio.utils.spotipy.Spotify.current_user_recently_played', return_value=mock_response) as mock_spotify:
        result = get_recent_songs("test_token")
        assert result == [
            {"artist": "Artist 1", "track": "Track 1", "played_at": "2024-03-01T10:00:00"},
            {"artist": "Artist 2", "track": "Track 2", "played_at": "2024-03-01T09:00:00"},
        ]

def test_get_recent_songs_error(client):
    with patch('new_radio.utils.spotipy.Spotify.current_user_recently_played', side_effect=Exception("Test Error")) as mock_spotify:
        result = get_recent_songs("test_token")
        assert result == []

def test_get_current_song_caching(client):
    mock_response = {
        'is_playing': True,
        'item': {
            'artists': [{'name': 'Test Artist'}],
            'name': 'Test Track',
            'album': {'images': [{'url': 'test_url'}]}
        }
    }
    with patch('new_radio.utils.spotipy.Spotify.current_user_playing_track', return_value=mock_response) as mock_spotify:
        # First call should fetch data
        result1 = get_current_song("test_token")
        assert result1 == {"artist": "Test Artist", "track": "Test Track", "album_art": "test_url"}
        mock_spotify.assert_called_once()

        # Second call within cache interval should return cached data
        result2 = get_current_song("test_token")
        assert result2 == {"artist": "Test Artist", "track": "Test Track", "album_art": "test_url"}
        mock_spotify.assert_called_once()  # Still only one call

        # Advance time past cache interval
        with patch('new_radio.utils.datetime') as mock_datetime:
          mock_datetime.now.return_value = datetime.now() + timedelta(seconds=61)
          # Third call should fetch data again
          result3 = get_current_song("test_token")
          assert result3 == {"artist": "Test Artist", "track": "Test Track", "album_art": "test_url"}
          assert mock_spotify.call_count == 2

def test_get_recent_songs_caching(client):
  mock_response = {
        "items": [
            {
                "track": {
                    "artists": [{"name": "Artist 1"}],
                    "name": "Track 1",
                },
                "played_at": "2024-03-01T10:00:00"
            }
        ]
    }
  with patch('new_radio.utils.spotipy.Spotify.current_user_recently_played', return_value=mock_response) as mock_spotify:
    #First call
    result1 = get_recent_songs("test_token")
    assert result1 == [{"artist": "Artist 1", "track": "Track 1", "played_at": "2024-03-01T10:00:00"}]
    mock_spotify.assert_called_once()

    #Second call
    result2 = get_recent_songs("test_token")
    assert result2 == [{"artist": "Artist 1", "track": "Track 1", "played_at": "2024-03-01T10:00:00"}]
    mock_spotify.assert_called_once()

    #Advance time
    with patch('new_radio.utils.datetime') as mock_datetime:
      mock_datetime.now.return_value = datetime.now() + timedelta(seconds=61)
      result3 = get_recent_songs("test_token")
      assert result3 == [{"artist": "Artist 1", "track": "Track 1", "played_at": "2024-03-01T10:00:00"}]
      assert mock_spotify.call_count == 2
