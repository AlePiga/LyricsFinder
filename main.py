import requests
import base64
import time
import os
import json
import lyricsgenius
import re
from dotenv import load_dotenv

# Configurazione API
load_dotenv()
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
GENIUS_ACCESS_TOKEN = os.getenv("GENIUS_ACCESS_TOKEN")

# Cache
CACHE_FILE = "music_cache.json"

# Inizializza Genius
genius = lyricsgenius.Genius(
    GENIUS_ACCESS_TOKEN, skip_non_songs=True, excluded_terms=["(Remix)", "(Live)"]
)


def get_spotify_token():
    # Ottiene token Spotify con cache
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            cache = json.load(f)
            if cache.get("spotify_token_expiry", 0) > time.time():
                return cache["spotify_token"]

    auth_url = "https://accounts.spotify.com/api/token"
    auth_header = base64.b64encode(
        f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode()
    ).decode()
    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    response = requests.post(
        auth_url, headers=headers, data={"grant_type": "client_credentials"}
    )
    token_data = response.json()

    # Aggiorna cache
    cache = {}
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            cache = json.load(f)

    cache.update(
        {
            "spotify_token": token_data["access_token"],
            "spotify_token_expiry": time.time() + 3600,
        }
    )

    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f)

    return token_data["access_token"]


def clean_lyrics(lyrics, song_title=None):
    # Pulisce il testo dai tag non necessari
    if not lyrics:
        return "Testo non trovato"

    # Se viene passato il titolo della canzone, rimuovi tutto prima di "<titolo> Lyrics" (case insensitive, con o senza spazi)
    if song_title:
        # Prepara pattern: "NOME DELLA CANZONE Lyrics" oppure "NOMEDELLACANZONELyrics" ecc.
        # Rimuove anche eventuali caratteri non alfanumerici/spazi tra titolo e "Lyrics"
        pattern = re.compile(
            rf"^(.*?){re.escape(song_title).replace(' ', r'[\s\-]*')}[\s\-]*lyrics[\s\-]*",
            re.IGNORECASE | re.DOTALL
        )
        lyrics = re.sub(pattern, "", lyrics, count=1)

    # Rimuove tutto prima (e incluso) 'Read More '
    lyrics = re.sub(r"^.*?Read More\s*", "", lyrics, flags=re.DOTALL)

    # Rimuove '[...]' eccessivi e righe vuote
    lyrics = re.sub(r"\[.*?\]\n?", "", lyrics)
    lyrics = re.sub(r"\n+", "\n", lyrics)

    return lyrics.strip()


def clean_title_for_genius(title):
    # Rimuove parti inutili dal titolo come ' - Remastered', ' - 2012 Mix', ecc
    return re.sub(
        r"\s*-\s*(\d{4}\s*)?(remaster(ed)?|mix|version|mono|stereo).*$",
        "",
        title,
        flags=re.IGNORECASE,
    ).strip()


def get_lyrics(track_title, artist_name):
    # Recupera il testo da Genius
    cleaned_title = clean_title_for_genius(track_title)
    try:
        song = genius.search_song(cleaned_title, artist_name)
        return clean_lyrics(song.lyrics) if song else "Testo non trovato"
    except Exception as e:
        return f"Errore: {str(e)}"
