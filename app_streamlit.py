import streamlit as st
import requests
from src.utils import navbar, footer

import streamlit as st
import requests
from src.utils import navbar, footer

# Base URL for the Flask API (adjust if needed)
BASE_URL = 'http://127.0.0.1:5001/api'

st.set_page_config(layout="wide")

# Load CSS
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# Display navbar
st.markdown(navbar(), unsafe_allow_html=True)

# Wrap content in a container
with st.container():

    st.title('RADIO')

    # Main layout: 3 columns
    col1, col2, col3 = st.columns(3)

    with col1:
        st.header('Currently Playing')
        try:
            current_song = requests.get(f'{BASE_URL}/current').json()
            if current_song:
              st.image(current_song['album_art'], width=250)
              st.subheader(current_song['track'])
              st.text(f"Artist: {current_song['artist']}")
            else:
              st.write("Not Playing")
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching current song: {e}")

    with col2:
        st.header("Search")
        search_query = st.text_input("Search for a song", key="search_input")
        if search_query:
            try:
                search_results = requests.get(f"{BASE_URL}/search?query={search_query}").json()
                st.write(search_results)  # Basic display for now
                # TODO: Display search results in a table
            except requests.exceptions.RequestException as e:
                st.error(f"Error during search: {e}")

    with col3:
        st.header("Submit Suggestion")
        with st.form("suggestion_form"):
            artist = st.text_input("Artist")
            track = st.text_input("Track")
            submitted = st.form_submit_button("Submit")
            if submitted:
                try:
                    response = requests.post(f"{BASE_URL}/submit", json={"artist": artist, "track": track})
                    if response.status_code == 201:
                        st.success("Suggestion submitted!")
                    else:
                        st.error("Error submitting suggestion.")
                except requests.exceptions.RequestException as e:
                    st.error(f"Error submitting suggestion: {e}")

    # Recent Songs (below the columns)
    st.header('Recently Played')
    try:
        recent_songs = requests.get(f'{BASE_URL}/recents').json()
        st.write(recent_songs) # Basic display
        # TODO:  Improve display of recent songs (e.g., table, cards)
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching recent songs: {e}")

# Display footer
st.markdown(footer(), unsafe_allow_html=True)
