from flask import Flask, redirect, request, session, url_for, render_template
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key')  # Change this to a secure key

SPOTIFY_CLIENT_ID = os.environ.get('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET')
SPOTIFY_REDIRECT_URI = os.environ.get('SPOTIFY_REDIRECT_URI')

# Spotify API endpoints
AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
API_URL = "https://api.spotify.com/v1/me"
PLAYLISTS_URL = "https://api.spotify.com/v1/me/playlists"

# Scopes required for your app
SCOPES = "user-library-read playlist-read-private playlist-modify-public"

@app.route('/')
def home():
    if not session.get('token'):
        return redirect(url_for('login'))
    return render_template('home.html')

@app.route('/login')
def login():
    auth_url = f"{AUTH_URL}?response_type=code&client_id={SPOTIFY_CLIENT_ID}&scope={SCOPES}&redirect_uri={SPOTIFY_REDIRECT_URI}"
    return redirect(auth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return "Error: No code found in request", 400

    # Exchange code for access token
    token_response = requests.post(TOKEN_URL, data={
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': SPOTIFY_REDIRECT_URI,
        'client_id': SPOTIFY_CLIENT_ID,
        'client_secret': SPOTIFY_CLIENT_SECRET
    })
    token_response_data = token_response.json()
    access_token = token_response_data.get('access_token')

    if access_token:
        session['token'] = access_token
        return redirect(url_for('home'))
    return "Error: Failed to retrieve access token", 400

@app.route('/profile')
def profile():
    token = session.get('token')
    if not token:
        return redirect(url_for('login'))

    headers = {
        'Authorization': f'Bearer {token}'
    }
    response = requests.get(API_URL, headers=headers)
    user_data = response.json()
    return render_template('profile.html', user_data=user_data)

@app.route('/playlists')
def playlists():
    token = session.get('token')
    if not token:
        return redirect(url_for('login'))

    headers = {
        'Authorization': f'Bearer {token}'
    }
    response = requests.get(PLAYLISTS_URL, headers=headers)
    playlists_data = response.json().get('items', [])
    return render_template('playlists.html', playlists=playlists_data)

@app.route('/add-track/<playlist_id>/<track_id>')
def add_track(playlist_id, track_id):
    token = session.get('token')
    if not token:
        return redirect(url_for('login'))

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    track_url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    response = requests.post(track_url, headers=headers, json={'uris': [f'spotify:track:{track_id}']})

    if response.status_code == 201:
        return redirect(url_for('playlists'))
    return "Error: Failed to add track", 400

if __name__ == '__main__':
    app.run(debug=True)
