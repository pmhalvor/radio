try:  # try/except to handle both local debugging and cloud running (maybe clean up?)
    from authorize import get_token 
except:
    from .authorize import get_token 
from datetime import datetime
import io, json, logging
from urllib import response
import pandas as pd 
import requests as r
import os 
import pickle

real_path = os.path.realpath(__file__)
dir_path = os.path.dirname(real_path)
ROOT = os.environ.get("ROOT")
MAX_ID_COUNT=50

####### DATA WRANGLING #############
def load_df(root=None, cleaned=False, end=False) -> pd.DataFrame:
    if root is None:
        root = ROOT

    suffix = "_cleaned" if cleaned else ""

    if os.path.exists(f'{root}/data/history{suffix}.csv'):
        df = pd.read_csv(f'{root}/data/history{suffix}.csv')
        print("loaded from", f'{root}/data/history{suffix}.csv')
    else:
        df = pd.read_csv(f'~/data/history{suffix}.csv')
        print("loaded from", f'~/data/history{suffix}.csv')
    
    max_played_at = max(df["played_at"])

    # get cleaned if current df is dirty
    if not end:
        if ("<<<<<<" in max_played_at) or (">>>>>>>" in max(df["played_at"])) or ("=======" in max(df["played_at"])):
            df, max_played_at = load_df(root, cleaned=True, end=True)  # break any recursivity
    else:
        print("Ending due to recursive call. Check that history_cleaned.csv really is clean... ")

    print("Max played at", max_played_at)
    return df, max_played_at



# Convert json data to dataframe
def json_to_df(data=None, latest=None) -> pd.DataFrame:
    '''
    typical josn data format:
    '''
    if not isinstance(data, dict):
        try:
            data = data.json()              # This needs to be cleaned up 
        except:
            print("Problem converting data of type {} to dict".format(type(data)))
            return None

    new_entries = pd.DataFrame(columns=['id','played_at','artist','name'])
    if data:
        for song in reversed(data['items']):
            played_at = song['played_at']
            name = song['track']['name'].replace(',','')

            if latest<played_at: #datetime.strptime(played_at, '%Y-%m-%dT%H:%M:%S.%fZ'):
                song_id = song['track']['id']
                artist = song['track']['artists'][0]['name'].replace(',','')

                # Build new entry as dictionary
                new_entry = {
                    'played_at': played_at,
                    'id': song_id,
                    'artist': artist,
                    'name': name 
                    }

                
                new_entries = new_entries.append(new_entry, ignore_index=True) # add entry to df
                try:
                    logging.info(f'New entry added: {new_entry}.')
                    print(f'New entry added: {new_entry}.')
                except:
                    logging.info('New entry added, but includes invalid character in name.')
                    print('New entry added, but includes invalid character in name.')
            else:
                logging.info(f'Song {name} played at {played_at} already registered.')
                print(f'Song {name} played at {played_at} already registered.')
                pass

    return new_entries


# Combine dataframes
def combine_dfs(csv_df=None, new_df=None) -> pd.DataFrame:
    if new_df.size == 0:
        return csv_df
    return csv_df.append(new_df, ignore_index=True)


# Convert dataframe to csv
def df_to_csv(df=None) -> str:
    try:
        if os.path.exists(f'{ROOT}/data/history.csv'):

            csv_str = df.to_csv(f'{ROOT}/data/history.csv', index=False)
        else:
            csv_str = df.to_csv('~/data/history.csv', index=False)

        return csv_str
    except:
        return df
#####################################


#####    API CALLS     ##############
# Get currently playing
def get_current(token=None) -> dict:
    if not token:
        token = get_token()
    # URL = "https://api.spotify.com/v1/me/player"  # api-endpoint for current playback
    URL = "https://api.spotify.com/v1/me/player/currently-playing"  # api-endpoint for current playback
    HEAD = {'Authorization': 'Bearer '+token}     # provide auth. crendtials
    content = r.get(url=URL, headers=HEAD)
    if content.status_code == 200:
        return content.json()
    else:
        return {}


# Request recently played
def get_recents(token=None) -> dict:
    if not token:
        token = get_token()
    URL = "https://api.spotify.com/v1/me/player/recently-played"    # api-endpoint for recently played
    HEAD = {'Authorization': 'Bearer '+token}                       # provide auth. crendtials
    PARAMS = {'limit':50}	                                        # default here is 20
    content = r.get(url=URL, headers=HEAD, params=PARAMS)
    if content.status_code == 200:
        return content.json()
    return {}


# Get list of tracks from ids
def get_tracks(token=None, batch_id_str=None) -> dict:
    tracks = {}

    URL = "https://api.spotify.com/v1/tracks"    # api-endpoint for recently played  
    HEAD = {'Authorization': 'Bearer '+token}    # provide auth. crendtials
    PARAMS = {'ids': batch_id_str}

    data = r.get(url=URL, headers=HEAD, params=PARAMS).json()

    if data.get("tracks") is not None:
        tracks = data['tracks']

    return tracks


def get_durations(id_list = [], token=None, store=True):
    """
    Should both load the previously stored duraitons and join with new durations.

    """
    pth = os.path.join(ROOT, "data", 'durations.csv')

    # load durations pickle
    # with open(pth, 'rb') as f:
    #    durations = pickle.load(f)

    # load durations as pandas df
    durations = pd.read_csv(pth, index_col=False)
    print(durations.tail())

    new_durations = pd.DataFrame({
        'id':list(set(id_list)),
    })

    durations = durations.merge(new_durations, on="id", how="outer")

    missing_ids = list((durations[durations.duration.isna()]).id)

    print(f'{len(missing_ids)} new ids to check')
    if len(missing_ids) > 0:
        if not token:
            token = get_token()

        batches = (len(missing_ids)//MAX_ID_COUNT) + 1
        print(f'Will be executing {batches} API call(s)')

        # batching the unstored indexes incase exceeds max
        for i in range(batches):
            print('Batch', i)
            if i==(batches-1):
                batch_ids = missing_ids[MAX_ID_COUNT*i:]  # last set of indices
                print("Checking indexes: {} -> {}".format(MAX_ID_COUNT*i, MAX_ID_COUNT*(i+1)) )
            else:
                batch_ids = missing_ids[MAX_ID_COUNT*i:MAX_ID_COUNT*(i+1)]  # forward indexing
                print("Checking indexes: {} -> {}".format(MAX_ID_COUNT*i, MAX_ID_COUNT*(i+1)) )

            batch_id_str = ','.join(batch_ids)

            tracks = get_tracks(token=token, batch_id_str=batch_id_str)

            if len(tracks) > 0:
                for track in tracks:
                    durations.loc[durations.id == track["id"], "duration"] = float(track['duration_ms'])

            else:
                print('No tracks in response')
                data = {
                    "python_log": {
                        "message": 'No tracks in response.',
                        "batch_ids_str": batch_id_str
                    }
                }
                with open(os.path.join(ROOT, 'durations_error_response.json'), 'w+') as f:
                    json.dump(data, f)

        # this only gets stored again when new ids are added
        print(f'Storing at {pth}')
        #durations.to_pickle(pth)
        durations.to_csv(pth, index=False)
        print('Success!')

    return durations

#####################################

####   OTHER TOOLS    #####
# Run all steps from this file
def run() -> bool:
    logging.info('Running song-history run() function.')
    token = get_token()
    data = get_recents(token=token)
    print("Recents: ", len(data))

    csv_df, latest = load_df()
    print("End of csv df:", csv_df.tail())

    spot_df = json_to_df(data=data, latest=latest)
    print("End of recent df", spot_df.tail())

    updated_df = combine_dfs(csv_df, spot_df)
    df_to_csv(updated_df)
    print("End up updated df", updated_df.tail())

    return updated_df


def print_current():
    token = get_token()
    data = get_current(token=token)
    print(data)

###########################


if __name__=='__main__':
    run()
    # print_current()
