import pytest
import pandas as pd
from src.history import load_df, json_to_df, combine_dfs, df_to_csv

@pytest.fixture
def sample_data():
    return [
        {
            "played_at": "2025-03-07T18:25:48.987Z",
            "uri": "spotify:track:0eS7dmrKdI0oy1rAR1k8Y5",
            "lead_artist": "Sheila's Disciples",
            # "artist": "Sheila's Disciples",  # in case we swap to multiple artists
            "track": "Harmonious Visit"
        },
        {
            "played_at": "2025-03-03T18:25:48.987Z",
            "uri": "spotify:track:3nCjMRvyfq0wgR3hDcAcWb",
            "lead_artist": "Coherent Energy",
            # "artist": "Coherent Energy",  
            "track": "Apogee"
        }
    ]

@pytest.fixture
def sample_csv_df():
    return pd.DataFrame({
        "played_at": ["2025-03-06T15:49:58.652Z"],
        "id": ["1Eolhana7nKHYpcYpdVcT5"],
        "artist": ["Jimi Hendrix"],
        "name": ["Little Wing"]
    })

@pytest.fixture
def sample_new_df():
    return pd.DataFrame({
        "played_at": ["2025-03-08T18:25:48.987Z"],
        "id": ["0eS7dmrKdI0oy1rAR1k8Y6"],
        "artist": ["Sheila's Disciples"],
        "name": ["Harmonious Visit 2"]
    })

def test_load_df(mocker):
    ## Goal: check that load df returns played_at and max_played_at
    # Assemble
    mocker.patch('os.path.exists', return_value=True) 
    mocker.patch('pandas.read_csv', return_value=pd.DataFrame({
        "played_at": ["2025-03-07T18:25:48.987Z", "2025-03-06T17:25:48.987Z"]
    }))
    
    # Act
    df, max_played_at = load_df()
    
    # Assert
    assert not df.empty
    assert max_played_at == "2025-03-07T18:25:48.987Z"

def test_json_to_df(sample_data):
    # Assemble
    latest = "2025-03-06T15:49:58.652Z" # in between data samples
    
    # Act
    new_entries = json_to_df(data=sample_data, latest=latest)
    
    # Assert
    assert not new_entries.empty
    assert new_entries.iloc[0]["played_at"] == "2025-03-07T18:25:48.987Z"
    assert len(new_entries) == 1 # only one entry is newer than latest

def test_combine_dfs(sample_csv_df, sample_new_df):
    # Assemble
    csv_df = sample_csv_df
    new_df = sample_new_df
    
    # Act
    combined_df = combine_dfs(csv_df=csv_df, new_df=new_df)
    
    # Assert
    assert len(combined_df) == 2
    assert combined_df.iloc[0]["artist"] == "Jimi Hendrix"
    assert combined_df.iloc[1]["artist"] == "Sheila's Disciples"

def test_df_to_csv(mocker, sample_csv_df):
    # Assemble
    mocker.patch('os.path.exists', return_value=True) # pretend to update file
    mocker.patch('pandas.DataFrame.to_csv', return_value="csv_string")
    
    # Act
    csv_str = df_to_csv(df=sample_csv_df)
    
    # Assert
    assert csv_str == "csv_string"

# def test_get_durations(mocker):
#     # TODO: update durations test when implemented
#     # Assemble
#     mocker.patch('os.path.exists', return_value=True)
#     mocker.patch('pandas.read_csv', return_value=pd.DataFrame({"id": ["0eS7dmrKdI0oy1rAR1k8Y5"], "duration": [None]}))
#     mocker.patch('src.history.get_tracks', return_value=[{"id": "0eS7dmrKdI0oy1rAR1k8Y5", "duration_ms": 155500}])
    
#     id_list = ["0eS7dmrKdI0oy1rAR1k8Y5"]
#     token = "sample_token"
    
#     # Act
#     durations = get_durations(id_list=id_list, token=token)
    
#     # Assert
#     assert not durations.empty
#     assert durations.iloc[0]["duration"] == 155500