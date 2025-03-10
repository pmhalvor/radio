import os
import pandas as pd
import plotly.express as px
import requests
import streamlit as st
import time

import logging
logging.basicConfig(level=logging.DEBUG)

# from src.utils import footer, refresher

# Base URL for the Flask API (adjust if needed)
API_HOST = os.environ.get("API_HOST", "radio_flask")
API_PORT = os.environ.get("API_PORT", "8888")
BASE_URL = f"http://{API_HOST}:{API_PORT}/api" #'http://127.0.0.1:8888/api'
logging.info(f"BASE_URL: {BASE_URL}")

st.set_page_config(
    # page_title="radio",  # not needed if embedded in webpage
    page_icon="local/static/img/Spotify.png",
    initial_sidebar_state= "collapsed",
    layout="wide",
    menu_items={
        "Get help": "https://github.com/pmhalvor/radio/wiki",
        "Report a bug": "https://github.com/pmhalvor/radio/issues",
        "About": "A Spotify webapp that display current and recent songs, "\
            "as well as some historical plots (if present). "\
            "See https://perhalvorsen.com/radio-app for a live example."
    },
)

# Load CSS
with open("local/static/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
st.markdown((
        "<script "
        'src="https://cdn.jsdelivr.net/npm/@iframe-resizer/child" '\
        'type="text/javascript"' 
        "async></script>"
    ), 
    unsafe_allow_html=True
)

# st.title('radio')

current_song = None
recent_songs = None
counter = 0
while (current_song, recent_songs) == (None, None):
    try:
        current_song = requests.get(f'{BASE_URL}/current').json()
        recent_songs = requests.get(f'{BASE_URL}/recents').json()
    except Exception as e:
        st.error(f"Error fetching data: {e}")

    counter += 1
    time.sleep(1)
    if counter > 10:
        break


# Convert recent songs to a DataFrame
recent_songs_df = pd.DataFrame(recent_songs)

# Wrap content in a container
with st.container():

    # Main layout: 3 columns
    col1, col2= st.columns(
        [1, 2],
        gap= 'large',
        vertical_alignment='top',
    )

    with col1:
        st.header('currently playing')
        try:
            current_song = requests.get(f'{BASE_URL}/current').json()
            if current_song:
              st.image(current_song['album_art'], use_container_width=True)
              st.subheader(current_song['track'])
              st.markdown(f"### {current_song['artist']}")
            #   st.markdown(refresher(current_song.get("duration", 10)), unsafe_allow_html=True)  # TODO fix refresh
            else:
              st.write("Not Playing")

            # st.markdown(refresher(current_song.get("duration", 1000)), unsafe_allow_html=True)

        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching current song: {e}")

    
    with col2:
        st.header("recent stats")
        # Create tabs
        tab1, tab2 = st.tabs(["plot", "data"])

        info_columns = [
            "artist",
            "track",
            "played_at",
            "url"
        ]
        with tab2:
            tab_df = recent_songs_df[[col for col in info_columns if col in recent_songs_df.columns]]
            st.dataframe(tab_df)

        with tab1:
            plottalbe_columns = [
                "popularity",
                "duration",
            ]

            # preprocess df
            tab_df = recent_songs_df[
                [col for col in plottalbe_columns if col in recent_songs_df.columns]
                + 
                [col for col in info_columns if col in recent_songs_df.columns]
            ].copy()

            tab_df["hover_info"] = tab_df["artist"] + " - " + tab_df["track"]
            
            tab_df["duration"] = tab_df["duration"] / 1000
            tab_df["played_at"] = pd.to_datetime(tab_df["played_at"])
            tab_df["played_at_numeric"] = tab_df["played_at"].astype("int64") // 10**9
            tab_df["played_at_numeric_norm"] = tab_df["played_at_numeric"] - tab_df["played_at_numeric"].min()
            tab_df = tab_df.sort_values("played_at_numeric")

            fig = px.scatter(
                tab_df,
                x="duration",
                y="popularity",
                color="played_at_numeric_norm",   
                color_continuous_scale="Blues",  
                size="popularity",    
                hover_name="hover_info",    
                hover_data={
                    "artist": False, 
                    "track": False,
                    "played_at": True, 
                    "duration": True, 
                    "popularity": True,
                    "played_at_numeric": False,
                    "played_at_numeric_norm": False,
                    "url": False,
                }, 
            )

            # postprocess fig
            fig.update_traces(marker=dict(line=dict(width=0)))
            fig.update_yaxes(showgrid=False, zeroline=False, tickvals=[])
            fig.update_xaxes(showgrid=False, zeroline=False, tickvals=[])
            fig.update_layout(
                xaxis_title="duration (s)",
                yaxis_title="popularity",
                coloraxis_colorbar=dict(
                    title="",
                    tickvals=[],
                    ticktext=[],
                )
            )
            fig.update_layout(
                plot_bgcolor = "rgb(0, 7, 30)",
                paper_bgcolor = "rgb(0, 7, 30)",
            )

            # show plot
            st.plotly_chart(fig, use_container_width=True)


with st.container():

    # Recent Songs (below the columns)
    st.header('recent albums')
    unique_albums = recent_songs_df.drop_duplicates(subset=['album_art'])

    album_images = unique_albums['album_art'].tolist()
    track_url = unique_albums['url'].tolist()

    album_url_list = [{"album":album, "url":url} for album, url in zip(album_images, track_url)]

    # Create a horizontal scrollable container
    scrollable_container = st.container()
    scrollable_container.markdown(
        """
        <style>
        .row{
            overflow: auto;
            white-space: nowrap;
            margin-left: 15px;
            margin-right: 15px;
            padding: 2%;
            background-color: rgb(75, 75, 75, 0.50);
            border-radius: 10px;
        }
        .row::-webkit-scrollbar{
            width: 10px;
        }
        .row::-webkit-scrollbar-thumb{
            background-color: rgb(70,70,70);
            border-radius: 5px;
        }
        .row::-webkit-scrollbar-track{
            border-bottom-left-radius: 5px;
            border-bottom-right-radius: 5px;
            background-color: black;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    html_str = '<div class="row">'
    for album_url_dict in album_url_list:
        html_str += \
            f'<a href="{album_url_dict["url"]}" >' \
            f'<img src="{album_url_dict["album"]}" width="250px"/>' \
            '</a>' 
    html_str += '</div>'
    scrollable_container.markdown(html_str, unsafe_allow_html=True)

# Display footer
# st.markdown(footer(), unsafe_allow_html=True)
