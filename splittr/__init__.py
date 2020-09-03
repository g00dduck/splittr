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

    @app.route('/')
    def login():
        if not session.get('uuid'):
            session['uuid'] = str(uuid.uuid4())
            print("Starting session with new UUID.")


        return render_template('login.html')

    @app.route('/authorize', methods=['POST'])
    def authorize():
        return display(spotipy.Spotify(auth_manager=auth_manager))

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