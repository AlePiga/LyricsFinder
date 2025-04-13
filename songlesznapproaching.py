import requests
import base64
import pyperclip

# Configurazione Spotify API (sostituisci con i tuoi dati)
CLIENT_ID = "31cfa63bc2fc4c57bb334acb78115712"
CLIENT_SECRET = "4de6d29c1ff4436ba240e41340f445b7"

def get_spotify_token():
    """Ottiene un token di accesso dall'API Spotify"""
    auth_url = "https://accounts.spotify.com/api/token"
    auth_header = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()

    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    
    response = requests.post(auth_url, headers=headers, data=data)
    return response.json()["access_token"]

def search_track(track_name, artist_name, token):
    """Cerca una traccia su Spotify e restituisce i dati"""
    search_url = "https://api.spotify.com/v1/search"
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "q": f"track:{track_name} artist:{artist_name}",
        "type": "track",
        "limit": 1
    }

    response = requests.get(search_url, headers=headers, params=params)
    return response.json()

def generate_js_object(track_data):
    """Genera l'oggetto JavaScript dal JSON di Spotify"""
    track = track_data["tracks"]["items"][0]
    return f"""let canzone = {{
    titolo: "{track['name']}",
    artista: {[a['name'] for a in track['artists']]},
    album: "{track['album']['name']}",
    durata_ms: {track['duration_ms']},
    immagine: "{track['album']['images'][0]['url'] if track['album']['images'] else ''}"
}};"""

def main():
    # Input utente
    track_name = input("Inserisci il titolo della canzone: ")
    artist_name = input("Inserisci l'artista: ")

    # Autenticazione e ricerca
    token = get_spotify_token()
    result = search_track(track_name, artist_name, token)

    if not result["tracks"]["items"]:
        print("❌ Canzone non trovata!")
        return

    # Genera e copia il JS
    js_code = generate_js_object(result)
    pyperclip.copy(js_code)
    print("\n✅ Oggetto copiato negli appunti! Ecco il risultato:\n")
    print(js_code)

if __name__ == "__main__":
    main()