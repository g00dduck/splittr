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

    @app.route('/display')
    def display(authorized_sp):
        tracks = authorized_sp.current_user_saved_tracks()

        return render_template("index.html", items=tracks['items'])

    @app.route('/logoff')
    @app.route('/signout')
    def log_off():
        os.remove(session_cache_path())
        session.clear()
        try:
            os.remove(session_cache_path())
        except OSError as e:
            print(f"Error: {e.filename}: {e.strerror}")

        return redirect('/')

    return app