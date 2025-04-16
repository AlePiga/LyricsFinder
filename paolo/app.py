from flask import Flask, request, jsonify, render_template
from main import get_random_track, get_lyrics, get_spotify_token
import requests

app = Flask(__name__)

def should_exclude_song(title):
    """Funzione helper per determinare se una canzone dovrebbe essere esclusa"""
    lower_title = title.lower()
    exclude_terms = [
        'remix',
        'acapella',
        'a cappella',
        'live',
        'instrumental',
        'hooligans version',  # schyeah
        'version',
        'acoustic',
        'world tour', # blackpink
        'arena tour', # blackpink
        'jp ver',  # blackpink
        'remastered'
    ]
    return any(term in lower_title for term in exclude_terms)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_songs')
def get_songs():
    artist = request.args.get('artist')
    if not artist:
        return jsonify({"error": "Artist parameter is required"}), 400

    token = get_spotify_token()
    if not token:
        return jsonify({"error": "Failed to get Spotify token"}), 500

    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Cerca l'artista
        search_url = "https://api.spotify.com/v1/search"
        response = requests.get(search_url, headers=headers, params={
            "q": artist, 
            "type": "artist", 
            "limit": 1
        })
        response.raise_for_status()
        
        artist_data = response.json()
        if not artist_data['artists']['items']:
            return jsonify({"error": "Artist not found"}), 404
            
        artist_id = artist_data['artists']['items'][0]['id']
        
        # Ottieni tutte le canzoni
        all_tracks = []
        albums_url = f"https://api.spotify.com/v1/artists/{artist_id}/albums"
        albums_response = requests.get(albums_url, headers=headers, params={
            "limit": 50,
            "include_groups": "album,single"
        })
        albums_response.raise_for_status()
        
        for album in albums_response.json()['items']:
            tracks_url = f"https://api.spotify.com/v1/albums/{album['id']}/tracks"
            tracks_response = requests.get(tracks_url, headers=headers)
            tracks_response.raise_for_status()
            
            for track in tracks_response.json()['items']:
                if artist_id in [a['id'] for a in track['artists']]:
                    # Applica il filtro
                    if not should_exclude_song(track['name']):
                        all_tracks.append({
                            "id": track['id'],
                            "title": track['name'],
                            "album": album['name'],
                            "artist": artist
                        })
        
        if not all_tracks:
            return jsonify({"error": "No valid tracks found after filtering"}), 404
            
        return jsonify(all_tracks)

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Spotify API error: {str(e)}"}), 500

@app.route('/get_lyrics')
def get_lyrics_route():
    song = request.args.get('song')
    artist = request.args.get('artist')
    
    if not song or not artist:
        return jsonify({"error": "Both song and artist parameters are required"}), 400
    
    try:
        lyrics = get_lyrics(song, artist)
        if not lyrics:
            return jsonify({"error": "Lyrics not found"}), 404
        return jsonify({"lyrics": lyrics})
    except Exception as e:
        return jsonify({"error": f"Failed to get lyrics: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=6969)