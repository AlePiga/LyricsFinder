# LyricsFinder
![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-2.x-lightgrey?logo=flask)
![Genius API](https://img.shields.io/badge/Genius%20API-enabled-yellow?logo=genius)
![License](https://img.shields.io/badge/License-MIT-green)

Un'applicazione web realizzata con Flask che consente di cercare una canzone su Spotify e recuperare automaticamente il testo da Genius.

## 🛠️ Requisiti

* Python 3.8+
* Un account Spotify Developer
* Un account Genius API

## 🚀 Funzionalità

* Ricerca brani su Spotify (titolo + artista)
* Recupero automatico della copertina dell'album
* Estrazione e pulizia dei testi da Genius.com
* API di ricerca con risposta in formato JSON
* Interfaccia web semplice via `index.html`

## 📦 Installazione

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
├── music_cache.json  # File creato temporaneamente per memorizzare il token di accesso a Spotify
├── .env              # Variabili d’ambiente (da creare)
```

## Pulizia dei testi

* Rimozione di tag `[Chorus]`, `[Verse 1]`, ecc.
* Eliminazione di righe vuote e testo promozionale
* Supporto alla rimozione di descrizioni aggiuntive di Genius

Fammi sapere se vuoi che lo adatti per GitHub Pages, Heroku o aggiunga un badge (come build status o API key required).
