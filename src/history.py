import json
import logging
import pandas as pd 
import os 

from authorize import get_token 
from spotify import get_current_song, get_recent_songs, get_tracks

ROOT = os.environ.get("ROOT")
MAX_ID_COUNT=50

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


def json_to_df(data=None, latest=None) -> pd.DataFrame:
    '''
    typical josn data format:
    '''

    new_entries = pd.DataFrame(columns=['id','played_at','artist','name'])
    if data:
        for song in reversed(data):
            played_at = song['played_at']


            if latest<played_at: # str in format '%Y-%m-%dT%H:%M:%S.%fZ'
                song_id = song['uri'].split(':')[-1]
                artist = song['lead_artist']
                # artists = song['artists']  # TODO use csv for multiple artists

                # Build new entry as dictionary
                new_entry = {
                    'played_at': played_at,
                    'id': song_id,
                    'artist': artist,
                    'name': song["track"] 
                    }

                # new_entries = new_entries.append(new_entry, ignore_index=True) # add entry to df
                new_entries = pd.concat(
                    (new_entries, pd.DataFrame(new_entry, index=[1]))
                ).reset_index(drop=True)
                try:
                    logging.info(f'New entry added: {new_entry}.')
                    print(f'New entry added: {new_entry}.')
                except (UnicodeEncodeError, UnicodeDecodeError) as e:
                    logging.info(f'New entry added, but includes invalid character in name.\n {e}')
                    print(f'New entry added, but includes invalid character in name.\n {e}')
            else:
                logging.info(f'Song {song["track"]} played at {played_at} already registered.')
                print(f'Song {song["track"]} played at {played_at} already registered.')
                pass

    return new_entries


def combine_dfs(csv_df=None, new_df=None) -> pd.DataFrame:
    if new_df.size == 0:
        return csv_df
    return pd.concat((csv_df, new_df), ignore_index=True).reset_index(drop=True)


def df_to_csv(df=None) -> str:
    try:
        if os.path.exists(f'{ROOT}/data/history.csv'):

            csv_str = df.to_csv(f'{ROOT}/data/history.csv', index=False)
        else:
            csv_str = df.to_csv('~/data/history.csv', index=False)

        return csv_str
    except Exception as e:
        logging.error(f'Error saving csv: {e}')
        print(f'Error saving csv: {e}')
        return df


def get_durations(id_list = [], token=None, store=True):
    """
    TODO Move to spotify.py
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
        # if not token:
        #     token = get_token()

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


def run() -> bool:
    logging.info('Running song-history run() function.')
    token = get_token()
    data = get_recent_songs(token=token)
    print("Recents: ", len(data))

    csv_df, latest = load_df()
    print("End of csv df:", csv_df.tail())

    spot_df = json_to_df(data=data, latest=latest)
    print("End of recent df", spot_df.tail())

    updated_df = combine_dfs(csv_df, spot_df)
    print("End up updated df", updated_df.tail())

    df_to_csv(updated_df)
    print("Success!")
    return updated_df


def print_current():
    token = get_token()
    data = get_current_song(token=token)
    print(data)


if __name__=='__main__':
    # print_current()

    run()
