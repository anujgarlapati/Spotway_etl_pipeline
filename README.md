# Spotway(Data Engineering Project): End to end ETL pipeline built using Python, AWS Cloud technologies(Lambda, S3, Glue, Athena, Cloudwatch) and Spotify Web API 
**What is Spotway?** Spotway is an end to end ETL(Extract, Transform, Load) pipeline built using Python, Spotify's Web API and AWS Cloud Technologies to see what songs are currently popular and trendy so that you are always up to date on the latest tunes.

## Tech Stack/Skils Used
1. Python
2. Spoity Web API
3. AWS Lambda
4. AWS S3
5. AWS Glue
6. AWS Cloudwatch
7. AWS Athena 

## Pipeline Architecture

The architecture diagram created below highlights and breaks down the ETL pipeline into different stages:

• We access the Spotify API and use Python to extract data from the API to build our pipeline. 

• We use AWS Cloudwatch to have a daily trigger which it is then extracted on AWS Lambda. 

• The extracted data is stored on a bucket in AWS S3. 

• The raw extracted data on S3 is placed on AWS Lambda once again and is transformed by the Lambda function and stored on S3. 

• The transformed data is crawled by AWS glue and can be accessed and used for data analytics on AWS Athena. 


![Screenshot 2023-05-29 at 4 00 19 PM](https://github.com/anujgarlapati/Spotway_etl_project/assets/59670482/87d78d5f-5d6d-427a-a332-d549373b04ab)

## Building the ETL Pipeline

Before starting to build the ETL pipeline, we must require access to the dataset. The dataset used for this data engineering project is Spotify's web API.
An account must be created to access this API, and this will allow us to get the credentials of both the client id and client secret. These tokens can be accessed as seen in the image below. 

![Screenshot 2023-05-31 at 2 58 51 PM](https://github.com/anujgarlapati/Spotway_etl_project/assets/59670482/95f33dc6-9b26-4d63-8a4d-dbb82b8ae93c)

## Spotify_extract_data_api.py

This Python file code is used to extract data from Spotify's web API. The code is run on AWS Lambda, where it is then stored in a lambda function and is used for the initial stages of our ETL pipeline. The code can be broken down as follows. 

The packages necessary for the lambda spotify extraction data api function:

```
import json
import os 
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import boto3
from datetime import datetime
```

Inside the lambda function both the client_id and client_secret are stored in AWS lambda environment variables to keep confidentiality. An object is created in order to extract data.

```
def lambda_handler(event, context):
    
    client_id = os.environ.get('client_id')
    client_secret = os.environ.get('client_secret')
    
    spotify_credentials = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    spotify_ob = spotipy.Spotify(client_credentials_manager=spotify_credentials)
    playlists = spotify_ob.user_playlists('spotify')
```

More specifically, we are extracting data from the global top 50 playlists where the URL is being extracted so that we access the playlist data. 

```
top50_playlist_link = "https://open.spotify.com/playlist/37i9dQZEVXbMDoHDwVN2tF"
top50_playlist_url = top50_playlist_link.split("/")[-1]

top50_data = spotify_ob.playlist_tracks(top50_playlist_url)
```

Boto3 provides a Python API for AWS cloud infrastructure services. In the following code, we store the raw data in a bucket in S3.

```
    client = boto3.client('s3')
    
    filename = "final_raw_data" + str(datetime.now()) + ".json"
    
    client.put_object(
        Bucket = "spotway-data-pipeline-project-anuj", 
        Key = "spotify_data_raw/process_required/" + filename, 
        Body = json.dumps(top50_data)
        )
   
```

The code is seen in AWS Lambda as follows. 

![Screenshot 2023-05-31 at 3 43 12 PM](https://github.com/anujgarlapati/Spotway_etl_project/assets/59670482/b65e82ca-b502-49eb-b872-821e27c627fd)

In Amazon Cloudwatch, we set a daily trigger as we are in need of extracting data once every day as the playlist data is ever-changing. This can be done by adding a trigger in the function overview.

![Screenshot 2023-05-31 at 3 46 04 PM](https://github.com/anujgarlapati/Spotway_etl_project/assets/59670482/15f829c6-b500-4eb8-a424-89ec4cb337c3)


## Spotify_data_transformation.py

Once raw data is extracted daily from Spoitfy's web API and stored on a bucket in S3, we must have a transformation function in AWS Lambda as the second part of our ETL pipeline. 

The first part of transforming the extracted data is that we are simply first looking into different characteristics of the data. We have multiple functions in this Python file, where the first lambda function focuses on the album data.
```
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
    
```  
Lambda function for artist data.

```
def spotifyartist(top50_data):
    
    top50_list_artist = []

    for line in top50_data['items']:
        for key, value in line.items():
            if key == "track":
                for artist in value['artists']:
                    artist_dict = {'artist_id': artist['id'], 'artist_name': artist['name'], 'url': artist['href'] }
                    top50_list_artist.append(artist_dict)

    return top50_list_artist
```

Lambda function for songs data.

```
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
```

Once we have each function for different parts of the playlist data we can then call each of the functions in the lambda handler where the transformed data will be placed in a bucket in S3. The code is below:

```
def lambda_handler(event, context):
    s3 = boto3.client('s3')
    Bucket = "spotway-data-pipeline-project-anuj"
    Key =  "spotify_data_raw/process_required/"
    
    spotify_data = []
    spotify_keys=[]
    
    for file in s3.list_objects(Bucket=Bucket, Prefix=Key)['Contents']:
        file_key = file['Key']
        if file_key.split('.')[-1] == "json":
            response = s3.get_object(Bucket=Bucket, Key = file_key)
            content = response['Body']
            jsonObject = json.loads(content.read())
            spotify_data.append(jsonObject)
            spotify_keys.append(file_key)
            
    for top50_data in spotify_data:
        top50_list_album = spotifyalbum(top50_data)
        top50_list_artist = spotifyartist(top50_data)
        song_list_top50 = spotifysongs(top50_data)
       
        top_50_album_df = pd.DataFrame.from_dict(top50_list_album)
        top_50_album_df = top_50_album_df.drop_duplicates(subset=['id'])
        
        top_50_artist_df = pd.DataFrame.from_dict(top50_list_artist)
        top_50_artist_df = top_50_artist_df.drop_duplicates(subset=['artist_id'])
        
        top50_song_df = pd.DataFrame.from_dict(song_list_top50)
        
        
        top_50_album_df['release_date'] = pd.to_datetime(top_50_album_df['release_date'])
        top50_song_df['song_added'] =  pd.to_datetime(top50_song_df['song_added'])
        
        top50_songkey = "spotify_transformed_data/spotify_songs_data/songs_transformed_data_"  + str(datetime.now()) + ".csv"
        song_buffer=StringIO()
        top50_song_df.to_csv(song_buffer, index = False)
        song_content = song_buffer.getvalue()
        s3.put_object(Bucket=Bucket, Key=top50_songkey, Body=song_content)
        
        top50_albumkey = "spotify_transformed_data/spotify_albums_data/album_transformed_data_"  + str(datetime.now()) + ".csv"
        album_buffer=StringIO()
        top_50_album_df.to_csv(album_buffer, index = False)
        album_content = album_buffer.getvalue()
        s3.put_object(Bucket=Bucket, Key=top50_albumkey, Body=album_content)
        
        top50_artistkey = "spotify_transformed_data/spotify_artist_data/artist_transformed_data_"  + str(datetime.now()) + ".csv"
        artist_buffer=StringIO()
        top_50_artist_df.to_csv(artist_buffer, index = False)
        artist_content = artist_buffer.getvalue()
        s3.put_object(Bucket=Bucket, Key=top50_artistkey, Body=artist_content)
        
    s3_resource = boto3.resource('s3')
    for key in spotify_keys:
        copy_source = {
            'Bucket': Bucket,
            'Key': key
        }
        s3_resource.meta.client.copy(copy_source, Bucket, 'spotify_data_raw/processed/' + key.split("/")[-1])    
        s3_resource.Object(Bucket, key).delete()

```

The trigger for spotify_data_transformation function is as follows:

![Screenshot 2023-05-31 at 4 28 57 PM](https://github.com/anujgarlapati/Spotway_etl_project/assets/59670482/905f1627-441d-4a43-b5ae-e4db3e75a07a)


## Loading the data in the ETL Pipeline

Once both the extraction and transformation phases are done for the ETL pipeline, the last and final phase of the ETL pipeline is to load the data. To load the data, we must use the crawler in AWS Glue to connect a datastore to create metadata tables. There are three different crawlers that we have created to load the data in a catalog, the artist, song, and album data. This can be seen in the image down below:


![Screenshot 2023-05-31 at 4 30 00 PM](https://github.com/anujgarlapati/Spotway_etl_project/assets/59670482/d32b2fdc-8a81-4106-b4b6-7344e7848482)

Once the data is loaded into a data catalog by AWS Glue's crawler, we can then access the data using AWS Athena for data analytics. We are able to perform a multitude of tasks which include even running SQL queries to sort and organize the data. This can be seen down below. 

![Screenshot 2023-05-31 at 4 39 07 PM](https://github.com/anujgarlapati/Spotway_etl_project/assets/59670482/f1acf069-0382-48d4-9615-097739553b22)


## Conclusion/Key Takeways

This project had deeply taught me how to create an ETL pipeline to extract, transform, and load data using AWS cloud technologies. Ultimately, I have learned thoroughly on how to use AWS Lambda, Glue, S3, Athena and Cloudwatch. 

**Note:** I have also cleaned the data using a jupyter notebook and this can be seen in the following Spotify_etl.ipynb file.
