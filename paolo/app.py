from flask import Flask, request, jsonify, render_template
from main import get_random_track, get_lyrics, get_spotify_token
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_songs')
def get_songs():
    artist = request.args.get('artist')
    token = get_spotify_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Cerca l'artista
    search_url = "https://api.spotify.com/v1/search"
    response = requests.get(search_url, headers=headers, params={
        "q": artist, 
        "type": "artist", 
        "limit": 1
    })
    artist_id = response.json()['artists']['items'][0]['id']
    
    # Ottieni tutte le canzoni
    all_tracks = []
    albums_url = f"https://api.spotify.com/v1/artists/{artist_id}/albums"
    albums_response = requests.get(albums_url, headers=headers, params={
        "limit": 50,
        "include_groups": "album,single"
    })
    
    for album in albums_response.json()['items']:
        tracks_url = f"https://api.spotify.com/v1/albums/{album['id']}/tracks"
        tracks_response = requests.get(tracks_url, headers=headers)
        for track in tracks_response.json()['items']:
            if artist_id in [a['id'] for a in track['artists']]:
                all_tracks.append({
                    "id": track['id'],
                    "title": track['name'],
                    "album": album['name'],
                    "artist": artist
                })
    
    return jsonify(all_tracks)

@app.route('/get_lyrics')
def get_lyrics_route():
    song = request.args.get('song')
    artist = request.args.get('artist')
    lyrics = get_lyrics(song, artist)
    return jsonify({"lyrics": lyrics})

if __name__ == '__main__':
    app.run(debug=True, port=5000)