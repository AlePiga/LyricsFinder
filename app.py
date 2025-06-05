from flask import Flask, request, jsonify, render_template
from main import get_lyrics, get_spotify_token
import requests

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/search_song")
def search_song():
    song_title = request.args.get("title")
    artist = request.args.get("artist")

    if not song_title or not artist:
        return (
            jsonify({"error": "Both song title and artist parameters are required"}),
            400,
        )

    try:
        # Ottieni il token Spotify
        token = get_spotify_token()
        if not token:
            return jsonify({"error": "Failed to get Spotify token"}), 500

        headers = {"Authorization": f"Bearer {token}"}

        # Cerca la canzone su Spotify
        search_url = "https://api.spotify.com/v1/search"
        response = requests.get(
            search_url,
            headers=headers,
            params={
                "q": f"track:{song_title} artist:{artist}",
                "type": "track",
                "limit": 1,
            },
        )
        response.raise_for_status()

        track_data = response.json()
        if not track_data["tracks"]["items"]:
            return jsonify({"error": "Song not found"}), 404

        track = track_data["tracks"]["items"][0]
        album_image = (
            track["album"]["images"][0]["url"] if track["album"]["images"] else None
        )

        # Ottieni il testo da Genius
        lyrics = get_lyrics(song_title, artist)
        if not lyrics or "non trovato" in lyrics.lower():
            return jsonify({"error": "Lyrics not found"}), 404

        return jsonify(
            {
                "title": track["name"],
                "artist": track["artists"][0]["name"],
                "album": track["album"]["name"],
                "album_image": album_image,
                "lyrics": lyrics,
            }
        )

    except Exception as e:
        return jsonify({"error": f"Error: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True, port=6969)
