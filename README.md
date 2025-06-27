# LyricsFinder

Un'applicazione web realizzata con Flask che consente di cercare una canzone su Spotify e recuperare automaticamente il testo da Genius.

## Requisiti

* Python 3.8+
* Un account Spotify
* Un account Genius

## Funzionalità

* Ricerca dei brani su Spotify, forniti titolo e artista
* Recupero automatico della copertina dell'album
* Estrazione e pulizia dei testi da Genius
* API di ricerca con risposta in formato JSON
* Interfaccia web clean e moderna via

## Installazione

1. **Clona il progetto**

   ```bash
   git clone https://github.com/tuo-username/lyrics-finder.git
   cd lyrics-finder
   ```

2. **Crea un ambiente virtuale (opzionale ma consigliato)**

   ```bash
   python -m venv venv
   source venv/bin/activate  # Su Windows: venv\Scripts\activate
   ```

3. **Installa le dipendenze**

   ```bash
   pip install -r requirements.txt
   ```

4. **Crea un file `.env` con le tue chiavi API**

   ```
   SPOTIFY_CLIENT_ID=tuo_spotify_client_id
   SPOTIFY_CLIENT_SECRET=tuo_spotify_client_secret
   GENIUS_ACCESS_TOKEN=tuo_genius_access_token
   ```

5. **Avvia il server**

   ```bash
   python app.py
   ```

   L'app sarà disponibile su `http://localhost:6969`

## Struttura del progetto

```
.
├── static/
│   ├── script.js
│   └── style.css
├── templates/
│   └── index.html
├── app.py
├── main.py
├── .env              # Variabili d’ambiente (da creare!)
└── music_cache.json  # File creato temporaneamente per memorizzare il token di accesso a Spotify
```

## Pulizia dei testi

* Rimozione di tag `[Chorus]`, `[Verse 1]`, ecc.
* Eliminazione di righe vuote e testo promozionale
* Supporto alla rimozione di descrizioni aggiuntive di Genius
