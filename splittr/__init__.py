import os
from datetime import date

import flask_session
import spotipy
import uuid
from flask import Flask, render_template, request, redirect, session

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('settings.py')
    app.jinja_env.globals['year'] = date.today().year
    flask_session.Session(app)

    caches_folder = './.spotify_caches/'
    if not os.path.exists(caches_folder):
        os.makedirs(caches_folder)

    def session_cache_path():
        return caches_folder + session.get('uuid')

    def get_auth_manager():
        auth_manager = spotipy.oauth2.SpotifyOAuth(scope='user-library-read',
            cache_path=session_cache_path(), show_dialog=True,
            client_id=app.config.get('SPOTIPY_CLIENT_ID'),
            client_secret=app.config.get('SPOTIPY_CLIENT_SECRET'))

        return auth_manager

    @app.route('/')
    def login():
        if not session.get('uuid'):
            session['uuid'] = str(uuid.uuid4())

        auth_manager = get_auth_manager()

        if not auth_manager.get_cached_token():
            # We're not logged in; render connect page!
            return render_template('login.html')
        else:
            # We ARE logged in; render display page!
            return display(spotipy.Spotify(auth_manager=auth_manager))

    @app.route('/connect', methods=['POST'])
    def connect():
        auth_manager = get_auth_manager()
        return redirect(auth_manager.get_authorize_url())

    @app.route('/authorize')
    def authorize():
        if request.args.get("code"):
            # Being redirected from Spotify auth page!
            auth_manager = get_auth_manager()
            auth_manager.get_access_token(request.args.get("code"))

            return display(spotipy.Spotify(auth_manager=auth_manager))
        else:
            # No code provided, returning to home
            return redirect('/')

    class LikedTrack():
        spotify_id = None
        name = None
        preview_url = None
        genres = None
        tempo = None
        time_signature = None
        energy = None
        loudness = None
        duration = None

    @app.route('/display')
    @app.route('/display/<offset>')
    def display(authorized_sp=None, offset=0):
        # Gets 50 tracks, starting with the given offset.
        # In the index page, make a pagination item that, like the action for connect,
        # renders this display with the given offset by every 50.
        if authorized_sp is None:
            authorized_sp = spotipy.Spotify(auth_manager=get_auth_manager())
        saved_tracks_info = authorized_sp.current_user_saved_tracks(limit=50)
        print(f"Given offset of {offset}!")
        print(f"{saved_tracks_info['total']} total liked tracks for this user!!")
        print(f"Looking at tracks {saved_tracks_info['offset']} through {len(saved_tracks_info['items'])}")

        liked_tracks = []
        for track in saved_tracks_info['items']:
            l = LikedTrack()
            l.spotify_id = track['track']['id']
            l.name = track['track']['name']
            l.preview_url = track['track']['preview_url']
            l.duration = track['track']['duration_ms'] / 60
            #print(f"\tTrack Name: {l.name}\tDuration: {l.duration}\tPreview URL: {l.preview_url}")
            liked_tracks.append(l)

        return render_template("index.html", items=liked_tracks)

    @app.route('/logoff')
    @app.route('/signout')
    def logoff():
        os.remove(session_cache_path())
        session.clear()
        try:
            os.remove(session_cache_path())
        except OSError as e:
            print(f"Error: {e.filename}: {e.strerror}")

        return redirect('/')

    return app