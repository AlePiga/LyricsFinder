import requests
import base64
import pyperclip
import random
import time
import os
import json
from tqdm import tqdm  # Progress bar

# Configurazione
CLIENT_ID = "31cfa63bc2fc4c57bb334acb78115712"
CLIENT_SECRET = "4de6d29c1ff4436ba240e41340f445b7"
CACHE_FILE = "spotify_cache.json"
MAX_ALBUMS = 1  # Limite album da analizzare (per velocità)

def get_spotify_token():
    """Ottiene token con cache (evita login continuo)"""
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            cache = json.load(f)
            if cache.get("token_expiry", 0) > time.time():
                return cache["token"]
    
    auth_url = "https://accounts.spotify.com/api/token"
    auth_header = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    headers = {"Authorization": f"Basic {auth_header}", "Content-Type": "application/x-www-form-urlencoded"}
    data = {"grant_type": "client_credentials"}
    
    response = requests.post(auth_url, headers=headers, data=data)
    token_data = response.json()
    
    # Salva in cache (token valido per 1 ora)
    with open(CACHE_FILE, "w") as f:
        json.dump({
            "token": token_data["access_token"],
            "token_expiry": time.time() + 3600
        }, f)
    
    return token_data["access_token"]

def get_random_track_fast(artist_id, token):
    """Versione ottimizzata con limite album"""
    headers = {"Authorization": f"Bearer {token}"}
    tracks = []
    
    # 1. Ottieni gli album (limitati a MAX_ALBUMS)
    albums_url = f"https://api.spotify.com/v1/artists/{artist_id}/albums"
    params = {
        "include_groups": "album,single",
        "limit": MAX_ALBUMS,
        "offset": random.randint(0, 20)  # Campionamento casuale
    }
    
    albums_response = requests.get(albums_url, headers=headers, params=params)
    albums = albums_response.json().get("items", [])
    
    # 2. Scansiona album con progress bar
    for album in tqdm(albums, desc="Scansione album"):
        tracks_url = f"https://api.spotify.com/v1/albums/{album['id']}/tracks"
        tracks_response = requests.get(tracks_url, headers=headers)
        for track in tracks_response.json().get("items", []):
            if artist_id in [a["id"] for a in track["artists"]]:
                tracks.append({
                    **track,
                    "album_name": album["name"],
                    "album_image": album["images"][0]["url"] if album["images"] else ""
                })
    
    return random.choice(tracks) if tracks else None

def main():
    artist_name = "Kendrick Lamar"
    token = get_spotify_token()
    
    # Trova ID artista (con cache)
    cache_key = f"artist_{artist_name.lower()}"
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            cache = json.load(f)
            if cache.get(cache_key):
                artist_id = cache[cache_key]
    
    if not locals().get("artist_id"):
        search_url = "https://api.spotify.com/v1/search"
        headers = {"Authorization": f"Bearer {token}"}
        params = {"q": artist_name, "type": "artist", "limit": 1}
        artist_data = requests.get(search_url, headers=headers, params=params).json()
        artist_id = artist_data["artists"]["items"][0]["id"]
        
        # Aggiorna cache
        with open(CACHE_FILE, "r+") as f:
            cache = json.load(f)
            cache[cache_key] = artist_id
            f.seek(0)
            json.dump(cache, f)
    
    # Ottieni traccia casuale (veloce)
    track = get_random_track_fast(artist_id, token)
    
    if not track:
        print("❌ Nessuna traccia trovata! Prova con un altro artista.")
        return
    
    js_object = f"""let canzone = {{
    titolo: "{track['name']}",
    artista: {[a['name'] for a in track['artists']]},
    album: "{track['album_name']}",
    durata_ms: {track['duration_ms']},
    immagine: "{track['album_image']}"
}};"""
    
    pyperclip.copy(js_object)
    print(f"\n✅ Trovata traccia casuale in {len(track)} album:\n{js_object}")

if __name__ == "__main__":
    main()