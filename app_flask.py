from flask import Flask, jsonify, request, redirect
from dotenv import load_dotenv
from datetime import datetime
from src.authorize import get_token, get_code_url, get_token_first_time
from src.utils import get_current_song, get_recent_songs
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)

@app.route('/api/current', methods=['GET'])
def api_current_song():
    token = get_token()
    if not token:
        return redirect(get_code_url())
    return jsonify(get_current_song(token))

@app.route('/api/recents', methods=['GET'])
def api_recent_songs():
    token = get_token()
    if not token:
        return redirect(get_code_url())
    return jsonify(get_recent_songs(token))

@app.route('/callback')
def callback():
    code = request.args.get('code')
    if code:
        get_token_first_time(code)
        return redirect('/')  # Redirect to the main page after authorization
    return "Error: No authorization code provided."

@app.route('/api/search', methods=['GET'])
def api_search():
    query = request.args.get('query')
    if not query:
        return jsonify([])

    try:
        # TODO: Implement search using a default token or application credentials, as it doesn't require user authorization.
        # results = spotify.search(q=query, type='track', limit=10)
        # tracks = []
        # for item in results['tracks']['items']:
        #     artist = item['artists'][0]['name']
        #     track = item['name']
        #     album = item['album']['name']
        #     tracks.append({"artist": artist, "track": track, "album": album})
        # return jsonify(tracks)
      return jsonify([]) # Return empty for now
    except Exception as e:
        print(f"Error searching Spotify: {e}")
        return jsonify([])

@app.route('/api/submit', methods=['POST'])
def api_submit():
    data = request.get_json()
    if not data or 'artist' not in data or 'track' not in data:
        return jsonify({"message": "Missing artist or track"}), 400

    try:
        new_page = {
            "artist": {"rich_text": [{"text": {"content": data['artist']}}]},
            "track": {"title": [{"text": {"content": data['track']}}]},
            "sub_date": {"date": {"start": datetime.now().isoformat()}}
        }
        # notion.pages.create(parent={"database_id": radio_suggestions_db_id}, properties=new_page)
        return jsonify({"message": "Suggestion submitted!"}), 201  # Temporarily return success
    except Exception as e:
        print(f"Error with suggestion submission: {e}")
        return jsonify({"message": "Error submitting suggestion"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=os.environ.get('PORT', 5001))  
