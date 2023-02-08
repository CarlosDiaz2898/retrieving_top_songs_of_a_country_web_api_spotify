import requests
import json
import base64
import pandas as pd

# Set up the client ID and secret
client_id = "{your client id}"
client_secret = "{your client secret}"

def access_token(id,secret):
    # Set up the headers
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    # Set up the data
    data = {
        "grant_type": "client_credentials",
        "scope": "app-remote-control"   
    }

    # Set up the credentials
    credentials = f"{client_id}:{client_secret}"

    # Encode the credentials
    encoded_credentials = base64.b64encode(credentials.encode("ascii"))

    # Add the encoded credentials to the headers
    headers["Authorization"] = f"Basic {encoded_credentials.decode('ascii')}"

    # Make the POST request
    response = requests.post("https://accounts.spotify.com/api/token", headers=headers, data=data)

    # Check the status code of the response
    if response.status_code != 200:
        raise ValueError(f"Failed to obtain access token. Error code: {response.status_code}")

    # Parse the response
    data = json.loads(response.text)

    # Extract the access token
    access_token = data["access_token"]

    print(access_token)
    return access_token

access_token=access_token(client_id,client_secret)

def playlist_per_country(access_token):
    
    # Set up the base URL and endpoint
    base_url = "https://api.spotify.com/v1"
    endpoint = "/search"
    
    
    # Set up the parameters
    params = {
        "q": "top songs in Colombia",
        "type": "playlist",
        "market":"co"
    }
    
    # Set up the headers
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    # Make the GET request
    response = requests.get(base_url + endpoint, headers=headers, params=params)
    
    # Check the status code of the response
    if response.status_code != 200:
        raise ValueError(f"Failed to search for the playlist. Error code: {response.status_code}")
    
    # Parse the response
    data = json.loads(response.text)
    
    # Extract the first playlist from the response
    playlist = data["playlists"]["items"][0]
    
    # Extract the playlist ID
    playlist_id = playlist["id"]
    return playlist_id

playlist_id=playlist_per_country(access_token)

    
def tracks_full(access_token,playlist_id):
    
    # Set up the base URL and endpoint
    base_url = "https://api.spotify.com/v1"
    endpoint = "/playlists/{playlist_id}/tracks"
    headers = {"Authorization": f"Bearer {access_token}"}
    limit = 50 # set the limit of tracks to retrieve

    # Make the GET request for the TOP songs
    params = {'limit': limit}
    response = requests.get(base_url + endpoint.format(playlist_id=playlist_id), headers=headers, params=params)

    # Check the status code of the response
    if response.status_code != 200:
        raise ValueError(f"Failed to retrieve the top songs of Colombia. Error code: {response.status_code}")

    # Parse the response
    data = json.loads(response.text)

    # Extract the track list
    tracks = data["items"]
    tracks_list=[]
    
    for track in tracks:
        tracks_list.append(track["track"])
        
    return tracks_list

tracks=tracks_full(access_token,playlist_id)

def tracks_genre_by_artist_id(tracks,access_token):
    
    artist_id_list=[]
    headers = {"Authorization": f"Bearer {access_token}"}

    
    for songs in tracks:
        artist_id=songs["artists"][0]["id"]
        #pedimos el genero por cada artista
        response = requests.get(f"https://api.spotify.com/v1/artists/{artist_id}",headers=headers)
        if response.status_code == 200:
            data = response.json()
            # print(data["genres"])
            artist_id_list.append(data["genres"])

        else:
            print("Error al buscar el artista")
            
            
    return artist_id_list
        
artists_genres=tracks_genre_by_artist_id(tracks, access_token)

def combinacion_genero_cancion(artists_genres,tracks):
    
    #dataframe a retornar
    df=pd.DataFrame()
    
    df = df.assign(Genero = artists_genres)
    
    nombres=[]
    for songs in tracks:
        artist_name=songs["artists"][0]["name"]
        #pedimos el genero por cada artista
        nombres.append(artist_name)
    df = df.assign(Artista=nombres)  
    
    nombres_cancion=[]
    for songs in tracks:
        song_name=songs["name"]
        #pedimos el genero por cada artista
        nombres_cancion.append(song_name)
    print(nombres_cancion)
        
        
    df = df.assign(Nombre=nombres_cancion) 
        
    return df

df=combinacion_genero_cancion(artists_genres, tracks)

def separar_por_genero(df):
    # Separar los géneros en varias filas
    #Utiliza la función "str.split()" para separar los géneros en una lista. 
    #Utiliza la función "explode()" para expandir la columna de géneros en varias filas, una para cada género.
    df = df.assign(genero=df['Genero'].str.split(',')).explode('Genero')
    
    grouped_df = df.groupby("Genero")
    
    for name, group in grouped_df:
        group.to_csv(name + ".csv", index=False)
    
    grouped_df_2 = df.groupby("Genero").agg({"Nombre": "count"}).rename(columns={"Nombre": "Cantidad"})
    
    return df,grouped_df_2
    
sep,count=separar_por_genero(df)






    
    