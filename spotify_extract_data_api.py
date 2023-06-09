import json
import os 
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import boto3
from datetime import datetime

def lambda_handler(event, context):
    
    client_id = os.environ.get('client_id')
    client_secret = os.environ.get('client_secret')
    
    spotify_credentials = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    spotify_ob = spotipy.Spotify(client_credentials_manager=spotify_credentials)
    playlists = spotify_ob.user_playlists('spotify')
    
    top50_playlist_link = "https://open.spotify.com/playlist/37i9dQZEVXbMDoHDwVN2tF"
    top50_playlist_url = top50_playlist_link.split("/")[-1]
    
    top50_data = spotify_ob.playlist_tracks(top50_playlist_url)
    
    client = boto3.client('s3')
    
    filename = "final_raw_data" + str(datetime.now()) + ".json"
    
    client.put_object(
        Bucket = "spotway-data-pipeline-project-anuj", 
        Key = "spotify_data_raw/process_required/" + filename, 
        Body = json.dumps(top50_data)
        )
    