from flask import Flask, jsonify, request, render_template
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__, template_folder="../local/static/templates")
CACHE_CODE_PATH = '.cache_code'
INTERNAL_API_HOST = os.environ.get('INTERNAL_API_HOST', 'localhost')
INTERNAL_API_PORT = os.environ.get('INTERNAL_API_PORT', 8888)

@app.route('/callback/authorized', methods=['GET'])
def callback_authorized():
    """
    Redirected to after user logs in and authorizes the app.
    """
    code = request.args.get('code', None)

    if code:
        # Store cached code
        with open(CACHE_CODE_PATH, 'w') as f:
            f.write(code)
        return render_template('success.html', code=code[:10]), 200
    else:
        return render_template('error.html', message='Failed to authenticate. Did you log in to Spotify?'), 404
    

@app.route('/callback/code', methods=['GET'])
def callback_code():
    """
    Checks for local cached code and returns it if found.
    """
    if os.path.exists(CACHE_CODE_PATH):
        with open(CACHE_CODE_PATH, 'r') as f:
            code = f.read()
        return jsonify({'message': 'Code found locally.', 'code': code}), 200
    else:
        return jsonify({'error': 'No code found locally.'}), 404


@app.route('/cache/clear', methods=['GET'])
def clear_cache():
    # Clear cached code
    if os.path.exists(CACHE_CODE_PATH):
        os.remove(CACHE_CODE_PATH)
    return jsonify({'message': 'Cache cleared!'}), 200


def run_flask_app():
    app.run(host=INTERNAL_API_HOST, port=INTERNAL_API_PORT, threaded=True)

if __name__ == '__main__':
    run_flask_app()
