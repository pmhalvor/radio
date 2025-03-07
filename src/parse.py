from datetime import datetime, timedelta

def parse_recents(data = None) -> list:
    content = []
    # extracting specific details
    if data:
        for song in data[:20]:
            track_url = song['track']['external_urls']['spotify']
            try:
                played_at = str(datetime.strptime(song['played_at'],  '%Y-%m-%dT%H:%M:%S.%fZ')
                            + timedelta(hours=1))[:-3]
            except:
                played_at = str(datetime.strptime(song['played_at'],  '%Y-%m-%dT%H:%M:%SZ')
                            + timedelta(hours=1))[:-3]
            name = song['track']['name'].replace(',','')
            song_id = song['track']['id']
            artist = song['track']['artists'][0]['name'].replace(',','')
            artist_url = song['track']['artists'][0]['external_urls']['spotify']

            content.append({'artist':artist, 'artist_url':artist_url, 
                            'name':name, 'played_at':played_at, 
                            'track_url': track_url})

    return content 


def parse_current(data = None) -> dict:
    content = {}

    if data and (data.get("currently_playing_type") == "track"):
        url 	 = data['item']['external_urls']['spotify']
        artwork  = data['item']['album']['images'][0]['url']
        track 	 = data['item']['name']
        artist 	 = data['item']['artists'][0]['name']
        duration = data['item']['duration_ms']
        progress = data['progress_ms'] #round(data['progress_ms']/duration*100, ndigits=1)
    
    elif data and (data.get("currently_playing_type") == "episode"):
        url	 = 'https://www.spotify.com' 
        artwork  = '/media/img/empty_album.png'
        track    = 'playing a podcast'
        artist   = ''
        duration = -1 
        progress = 0
    
    else:
        url	 = 'https://www.spotify.com' 
        artwork  = '/media/img/empty_album.png'
        track    = 'nothing playing'
        artist   = ''
        duration = -1 
        progress = 0

    content['url'] 	= url
    content['artwork'] 	= artwork
    content['track'] 	= track
    content['artist'] 	= artist
    content['duration'] = duration
    content['progress'] = progress

    return content
