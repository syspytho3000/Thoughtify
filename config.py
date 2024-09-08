import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'mysecretkey')
    SPOTIFY_CLIENT_ID = os.environ.get('77eea797ef1e4ba488685f15c3f5a88a')
    SPOTIFY_CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET')
