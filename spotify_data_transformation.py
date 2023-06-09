import json
import boto3
from datetime import datetime
from io import StringIO
import pandas as pd

def spotifyalbum(top50_data):
    
    top50_list_album = []
    
    for line in top50_data['items']:
        album_id_top50 = line['track']['album']['id']
        album_name_top50 = line['track']['album']['name']
        album_releasedate_top50 = line['track']['album']['release_date']
        album_totaltracks_top50 = line['track']['album']['total_tracks']
        album_url_top50 = line['track']['album']['external_urls']['spotify']
        
        # converting into dictonary 
        album_dict = {'id': album_id_top50, 'name': album_name_top50, 'release_date':album_releasedate_top50, 'total_tracks': album_totaltracks_top50, 'url': album_url_top50 }
        top50_list_album.append(album_dict)
        
    return top50_list_album
    
    
def spotifyartist(top50_data):
    
    top50_list_artist = []

    for line in top50_data['items']:
        for key, value in line.items():
            if key == "track":
                for artist in value['artists']:
                    artist_dict = {'artist_id': artist['id'], 'artist_name': artist['name'], 'url': artist['href'] }
                    top50_list_artist.append(artist_dict)

    return top50_list_artist
    
def spotifysongs(top50_data):
    song_list_top50= []

    for line in top50_data['items']:
        song_id_top50 = line['track']['id']
        song_name_top50 = line['track']['name']
        song_duration_top50 = line['track']['duration_ms']
        song_url_top50 = line['track']['external_urls']['spotify']
        song_popularity_top50 = line['track']['popularity']
        song_added = line['added_at']
        
        # converting into dictonary 
        song_dict = {'id': song_id_top50, 'name': song_name_top50, 'duration':song_duration_top50, 'url': song_url_top50, 'popularity': song_popularity_top50, 'song_added' : song_added }
        song_list_top50.append(song_dict)

    return song_list_top50