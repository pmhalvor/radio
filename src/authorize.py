import base64
import json
import os
import requests
import six
import time
import urllib.parse
import webbrowser

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATAPATH = '.data'
PORT = 8888

# Authorization for Spotify
def get_token() -> str:
    '''
    Steps:
        X get token from local file ".data"
        X check if access_token is expired:
            X it is expired:
                X call token url with correct parameters and headers
                X update .data with new tokens
        X return access token
    '''
    cache_token = get_cache_token()

    if is_token_expired(cache_token) or cache_token.get("token") in (None, "null"):
        cache_token = refresh_access_token(cache_token['refresh_token'])

    return cache_token['token']


# Read cached token from FileShare
def get_cache_token() -> dict:
    """
    Steps:
        X load local data
        X return payload
    """

    path = DATAPATH
    try:
        with open(path, 'r') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = get_token_first_time()

    return data
    # payload = {
    #     "refresh_token": data.get("refresh_token", None),
    #     "timestamp": data.get("timestamp", None),
    #     "token": data.get("token", None),
    #     "scope": data.get("scope", None),
    #     "expires_in": data.get("expires_in", None),
    #     "token_type": data.get("token_type", None),
    #     "access_token": data.get("access_token", None),
    # }

    # return payload


# Check if cached token is still valid
def is_token_expired(token_info) -> bool:
    """
    Steps:
        X get current time
        X measure difference between now and timestamp
        X create boolean about expired
            X fall back on setting expired true
    """
    now = int(time.time())

    try:
        time_difference = now - int(token_info["timestamp"])
        expired = time_difference > 3600
    except (TypeError, KeyError):
        expired = True  # Handle cases where timestamp is missing or invalid

    if token_info.get("token") in (None, "null"):
        expired = True

    return expired


# Refresh token from cache
def refresh_access_token(refresh_token) -> dict:
    '''
    Steps:
        X set correct payload (refresh_token)
        X set correct header  (client id and secret)
        X post request
        X convert response to json
        X update token_info in FileShare cache
        X return token info
    '''
    if not refresh_token:
      return {}
    # parameters for post request
    OAUTH_TOKEN_URL = "https://accounts.spotify.com/api/token"
    PAYLOAD = {
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token'
    }
    HEADERS = make_headers()

    # post request
    response = requests.post(
        url=OAUTH_TOKEN_URL,
        data=PAYLOAD,
        headers=HEADERS
    )
    token_info = response.json()

    print(f"Returned token info: \n {token_info}")
    # # Handle cases where refresh token might be missing
    # returned_refresh_token = token_info.get("refresh_token", refresh_token)
    # if "access_token" not in token_info:
    #     return {}

    # # payload = {  # TODO check behavior on refresh token
    # #     "refresh_token": returned_refresh_token,
    # #     "token": token_info["access_token"],
    # #     "timestamp": int(time.time())
    # # }

    # store tokens for later
    store_renewed_token(token_info)

    return token_info


# Make header for token request
def make_headers() -> dict:
    client_id = os.environ.get('SPOTIFY_CLIENT_ID')         # Spotify cliient id stored as local env. var.
    client_secret = os.environ.get('SPOTIFY_CLIENT_SECRET') # Spotify client secret stored as local env. var.

    # base64 encoded string
    client = base64.b64encode(
        six.text_type(f'{client_id}:{client_secret}').encode('ascii')
    )
    return {"Authorization": f"Basic {client.decode('ascii')}", "Content-Type": "application/x-www-form-urlencoded"}


# Store the renewed token locally
def store_renewed_token(token_info):
    path = DATAPATH
    with open(path, 'w') as f:
        json.dump(token_info, f, indent=4)
    return True


# Get first token with access code
def get_token_first_time(code=None) -> dict:
    '''
    Steps:
        X set correct payload (refresh_token)
        X set correct header  (client id and secret)
        X post request
        X convert response to json
        X update token_info in FileShare cache
        X return token info
    '''
    
    if not code:
        code = get_code()
    
    # parameters for post request
    OAUTH_TOKEN_URL = "https://accounts.spotify.com/api/token"
    PAYLOAD = {
        'grant_type': 'authorization_code',
        'redirect_uri': f'http://localhost:{PORT}/callback/authorized',  # defined in Spotify Developer Dashboard
        'code': code,
    }
    HEADERS = make_headers()

    # post request
    response = requests.post(
        url=OAUTH_TOKEN_URL,
        data=PAYLOAD,
        headers=HEADERS
    )
    token_info = response.json()
    print(f"Returned token info: \n {token_info}")

    if "error" in token_info:
        quit() 
    else: 
        breakpoint() 
    
    if "access_token" not in token_info:
        return {}
    
    # add needed key-values to token info before storing
    token_info["timestamp"] = int(time.time())
    token_info["token"] = token_info["access_token"]

    # store for later use
    store_renewed_token(token_info)

    return token_info


# Build url to generate access code (cannot use requests to call)
def get_code_url():
    """
    Can not call requests to get access code.
    """

    # parameters for post request
    OAUTH_TOKEN_URL = "https://accounts.spotify.com/authorize"
    PAYLOAD = {
        'client_id': os.environ.get('SPOTIFY_CLIENT_ID'),
        'scope': 'user-read-currently-playing user-read-recently-played',
        'redirect_uri': f'http://localhost:{PORT}/callback/authorized',  # defined in Spotify Developer Dashboard
        'response_type': 'code'
    }
    authorization_url = f"{OAUTH_TOKEN_URL}?{urllib.parse.urlencode(PAYLOAD)}"
    return authorization_url


def get_code():
    authorization_url = get_code_url()
    webbrowser.open(authorization_url, 2)  # open browser to get code

    code = None 
    counter = 0
    while code is None:
        code = requests.get(f'http://localhost:{PORT}/callback/code').json().get('code', None)
        
        time.sleep(1)
        counter += 1
        if counter > 5:  # TODO: # wait up to 10 seconds
            break
        
    requests.get(f'http://localhost:{PORT}/cache/clear')  # clean up credentials
    
    return code


if __name__ == "__main__":
    # print(get_code())
    print(get_token())