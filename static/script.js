document.addEventListener('DOMContentLoaded', () => {
    const songTitleInput = document.getElementById('song-title');
    const artistNameInput = document.getElementById('artist-name');
    const searchButton = document.getElementById('search-button');
    const loadingElement = document.getElementById('loading');
    const errorMessageElement = document.getElementById('error-message');
    const resultContainer = document.getElementById('result-container');
    const albumImageElement = document.getElementById('album-image');
    const songTitleDisplay = document.getElementById('song-title-display');
    const artistNameDisplay = document.getElementById('artist-name-display');
    const albumNameDisplay = document.getElementById('album-name-display');
    const lyricsElement = document.getElementById('lyrics');

    // Funzione per mostrare un messaggio di errore
    function showError(message) {
        errorMessageElement.textContent = message;
        errorMessageElement.classList.remove('hidden');
        resultContainer.classList.add('hidden');
        loadingElement.classList.add('hidden');
    }

    // Funzione per cercare la canzone
    async function searchSong() {
        const songTitle = songTitleInput.value.trim();
        const artistName = artistNameInput.value.trim();

        if (!songTitle || !artistName) {
            showError('Per favore, inserisci sia il titolo della canzone che il nome dell\'artista.');
            return;
        }

        // Nascondi eventuali risultati o errori precedenti
        resultContainer.classList.add('hidden');
        errorMessageElement.classList.add('hidden');

        // Mostra l'indicatore di caricamento
        loadingElement.classList.remove('hidden');

        try {
            const response = await fetch(`/search_song?title=${encodeURIComponent(songTitle)}&artist=${encodeURIComponent(artistName)}`);
            const data = await response.json();

            // Nascondi l'indicatore di caricamento
            loadingElement.classList.add('hidden');

            if (response.ok) {
                // Mostra i risultati
                songTitleDisplay.textContent = data.title;
                artistNameDisplay.textContent = data.artist;
                albumNameDisplay.textContent = `Album: ${data.album}`;
                lyricsElement.textContent = data.lyrics;

                // Imposta l'immagine dell'album se disponibile
                if (data.album_image) {
                    albumImageElement.src = data.album_image;
                    albumImageElement.alt = `Copertina di ${data.album}`;
                } else {
                    // Immagine placeholder se non disponibile
                    albumImageElement.src = 'https://via.placeholder.com/150?text=No+Image';
                    albumImageElement.alt = 'Copertina non disponibile';
                }

                resultContainer.classList.remove('hidden');
            } else {
                showError(data.error || 'Si è verificato un errore durante la ricerca della canzone.');
            }
        } catch (error) {
            console.error('Error:', error);
            showError('Si è verificato un errore di connessione. Riprova più tardi.');
        }
    }

    // Funzione per ottenere la cronologia dal localStorage
    function getHistory() {
        return JSON.parse(localStorage.getItem('searchHistory') || '[]');
    }

    // Funzione per salvare una nuova ricerca
    function saveToHistory(song, artist) {
        const history = getHistory();
        const now = new Date();
        history.unshift({
            song,
            artist,
            datetime: now.toLocaleString('it-IT', { hour12: false })
        });
        // Limita la cronologia a 10 elementi
        localStorage.setItem('searchHistory', JSON.stringify(history.slice(0, 10)));
    }

    // Funzione per rimuovere una voce dalla cronologia
    function removeFromHistory(index) {
        const history = getHistory();
        history.splice(index, 1);
        localStorage.setItem('searchHistory', JSON.stringify(history));
        renderHistory();
    }

    // Funzione per mostrare la cronologia
    function renderHistory() {
        const history = getHistory();
        const list = document.getElementById('history-list');
        list.innerHTML = '';
        if (history.length === 0) {
            list.innerHTML = `<li class="p-4 text-gray-400 text-center">Nessuna ricerca recente.</li>`;
            return;
        }
        history.forEach((item, idx) => {
            const li = document.createElement('li');
            li.className = "flex flex-col md:flex-row md:items-center justify-between p-4 hover:bg-gray-50 transition group";
            li.innerHTML = `
                <div>
                    <span class="font-semibold text-spotify-green">${item.song}</span>
                    <span class="text-gray-500">di</span>
                    <span class="font-medium text-gray-700">${item.artist}</span>
                </div>
                <div class="flex items-center gap-3 mt-2 md:mt-0">
                    <span class="text-sm text-gray-400">${item.datetime}</span>
                    <button title="Rimuovi"
                        class="ml-2 text-red-500 hover:text-white hover:bg-red-500 rounded-full w-7 h-7 flex items-center justify-center transition"
                        data-index="${idx}">
                        <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 pointer-events-none" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                        </svg>
                    </button>
                </div>
            `;
            list.appendChild(li);
        });

        // Aggiungi event listener ai bottoni X
        list.querySelectorAll('button[data-index]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const idx = parseInt(btn.getAttribute('data-index'));
                removeFromHistory(idx);
            });
        });
    }

    // Modifica la funzione di ricerca per salvare la cronologia
    document.getElementById('search-button').addEventListener('click', function () {
        const song = document.getElementById('song-title').value.trim();
        const artist = document.getElementById('artist-name').value.trim();
        if (!song || !artist) return;
        saveToHistory(song, artist);
        renderHistory();
        searchSong();
    });

    // Event listener per il pulsante di ricerca
    searchButton.addEventListener('click', searchSong);

    // Event listener per la pressione del tasto Enter nei campi di input
    songTitleInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') searchSong();
    });

    artistNameInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') searchSong();
    });

    // Mostra la cronologia al caricamento della pagina
    document.addEventListener('DOMContentLoaded', renderHistory);
});