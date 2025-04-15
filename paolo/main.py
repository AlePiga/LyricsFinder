import requests
import base64
import pyperclip
import random
import time
import os
import json
from tqdm import tqdm
import lyricsgenius
import re

# Configurazione API
SPOTIFY_CLIENT_ID = "31cfa63bc2fc4c57bb334acb78115712"
SPOTIFY_CLIENT_SECRET = "4de6d29c1ff4436ba240e41340f445b7"
GENIUS_ACCESS_TOKEN = "tzf8Qp6EzgqvorMeLhDNYejfgaWINynJEYCkxS85nJxPUnHSEmyE81r75rRprxpi"

# Cache
CACHE_FILE = "music_cache.json"
MAX_ALBUMS = 5  # Limite album da analizzare

# Inizializza Genius
genius = lyricsgenius.Genius(GENIUS_ACCESS_TOKEN, skip_non_songs=True, excluded_terms=["(Remix)", "(Live)"])

def get_spotify_token():
    # Ottiene token Spotify con cache# 
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            cache = json.load(f)
            if cache.get("spotify_token_expiry", 0) > time.time():
                return cache["spotify_token"]
    
    auth_url = "https://accounts.spotify.com/api/token"
    auth_header = base64.b64encode(f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode()).decode()
    headers = {"Authorization": f"Basic {auth_header}", "Content-Type": "application/x-www-form-urlencoded"}
    
    response = requests.post(auth_url, headers=headers, data={"grant_type": "client_credentials"})
    token_data = response.json()
    
    # Aggiorna cache
    cache = {}
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            cache = json.load(f)
    
    cache.update({
        "spotify_token": token_data["access_token"],
        "spotify_token_expiry": time.time() + 3600
    })
    
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f)
    
    return token_data["access_token"]

def get_random_track(artist_name):
    # Ottiene una traccia casuale dall'artista escludendo album live# 
    token = get_spotify_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Cerca artista
    cache_key = f"artist_{artist_name.lower()}"
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            cache = json.load(f)
            if cache.get(cache_key):
                artist_id = cache[cache_key]
    
    if not locals().get("artist_id"):
        search_url = "https://api.spotify.com/v1/search"
        response = requests.get(search_url, headers=headers, params={
            "q": artist_name, 
            "type": "artist", 
            "limit": 1
        })
        artist_id = response.json()["artists"]["items"][0]["id"]
        
        # Salva in cache
        with open(CACHE_FILE, "r+") as f:
            cache = json.load(f)
            cache[cache_key] = artist_id
            f.seek(0)
            json.dump(cache, f)
    
    # Ottieni TUTTI gli album (aumenta il limite)
    all_albums = []
    albums_url = f"https://api.spotify.com/v1/artists/{artist_id}/albums"
    params = {
        "include_groups": "album,single",
        "limit": 50,  # Aumentato da 5 a 50
        "offset": 0
    }
    
    while True:
        response = requests.get(albums_url, headers=headers, params=params)
        data = response.json()
        all_albums.extend(data["items"])
        
        if not data.get("next"):
            break
        params["offset"] += params["limit"]
    
    # Filtra album live
    non_live_albums = [
        album for album in all_albums 
        if not any(word in album["name"].lower() for word in ["live", "concert", "stage", "performance"])
    ]
    
    if not non_live_albums:
        print("⚠️ Nessun album studio trovato, provo con altri album")
        non_live_albums = all_albums
    
    # Seleziona casualmente MAX_ALBUMS album dal pool filtrato
    selected_albums = random.sample(non_live_albums, min(MAX_ALBUMS, len(non_live_albums)))
    
    # Scansiona album selezionati
    all_tracks = []
    for album in tqdm(selected_albums, desc="Scansione album"):
        tracks_url = f"https://api.spotify.com/v1/albums/{album['id']}/tracks"
        tracks_response = requests.get(tracks_url, headers=headers)
        tracks = tracks_response.json().get("items", [])
        
        for track in tracks:
            track_name_lower = track["name"].lower()
            if artist_id in [a["id"] for a in track["artists"]]:
                if "instrumental" in track_name_lower:
                    continue # Skippa tracce strumentali
                all_tracks.append({
                    "title": track["name"],
                    "artist": artist_name,
                    "album": album["name"],
                    "duration_ms": track["duration_ms"],
                    "spotify_id": track["id"],
                    "is_live": any(word in album["name"].lower() for word in ["live", "concert"])
                })

    if not all_tracks:
        return None
        
    return random.choice(all_tracks)

def clean_lyrics(lyrics):
    # Pulisce il testo dai tag non necessari
    if not lyrics:
        return "Testo non trovato"
    lyrics = re.sub(r'^.*?Lyrics', '', lyrics, flags=re.DOTALL)
    lyrics = re.sub(r'\[.*?\]\n?', '', lyrics)
    lyrics = re.sub(r'\n+', '\n', lyrics)
    return lyrics.strip()

def clean_title_for_genius(title):
    # Rimuove parti inutili dal titolo come ' - Remastered', ' - 2012 Mix', ecc
    return re.sub(r'\s*-\s*(\d{4}\s*)?(remaster(ed)?|mix|version|mono|stereo).*$', '', title, flags=re.IGNORECASE).strip()

def get_lyrics(track_title, artist_name):
    # Recupera il testo da Genius
    cleaned_title = clean_title_for_genius(track_title)
    try:
        song = genius.search_song(cleaned_title, artist_name)
        return clean_lyrics(song.lyrics) if song else "Testo non trovato"
    except Exception as e:
        return f"Errore: {str(e)}"

def get_lyrics_with_retry(artist_name, max_attempts=3):
    # Ottiene una canzone casuale e il suo testo con tentativi di fallback
    attempt = 0
    while attempt < max_attempts:
        attempt += 1
        print(f"\n🔍 Tentativo {attempt}/{max_attempts}")
        
        track = get_random_track(artist_name)
        if not track:
            print("❌ Nessuna traccia trovata!")
            continue
            
        print(f"🎵 Selezionata: {track['title']}")
        
        lyrics = get_lyrics(track["title"], artist_name)
        if "non trovato" not in lyrics.lower() and "errore" not in lyrics.lower():
            return track, lyrics
            
        print(f"⚠️ Testo non trovato per '{track['title']}', riprovo...")
    
    return None, "Testo non trovato dopo N tentativi"

def get_all_songs(artist_name):
    artist_dir = os.path.join("songs", artist_name)
    if not os.path.isdir(artist_dir):
        return []

    songs = []
    for filename in os.listdir(artist_dir):
        if filename.endswith(".json"):
            with open(os.path.join(artist_dir, filename), "r", encoding="utf-8") as f:
                data = json.load(f)
                songs.append(data)
    return songs

def get_lyrics_by_title(artist_name, title):
    songs = get_all_songs(artist_name)
    for song in songs:
        if song["title"].lower() == title.lower():
            return song.get("lyrics", "")
    return None

def main():
    artist_name = input("Inserisci il nome dell'artista: ")
    track, lyrics = get_lyrics_with_retry(artist_name)
    
    if track:
        print(f"\n✅ Testo trovato per {track['title']}!")
        print(f"\n📜 Testo completo:\n{lyrics}")
        pyperclip.copy(f"{track['title']}\n\n{lyrics}")
        print("\n✅ Testo copiato negli appunti!")
    else:
        print(lyrics)

if __name__ == "__main__":
    main()