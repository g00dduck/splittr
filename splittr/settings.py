from os import environ

SPOTIPY_CLIENT_ID=environ.get('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET=environ.get('SPOTIPY_CLIENT_SECRET')
SPOTIPY_REDIRECT_URI=environ.get('SPOTIPY_REDIRECT_URI')

SECRET_KEY=environ.get('SECRET_KEY')
SESSION_TYPE=environ.get('SESSION_TYPE')
SESSION_FILE_DIR=environ.get('SESSION_FILE_DIR')
