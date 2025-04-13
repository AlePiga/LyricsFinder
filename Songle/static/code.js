async function cercaTesto() {
    const titolo = document.getElementById('titolo').value;
    const artista = document.getElementById('artista').value;
    const lyricsDiv = document.getElementById('lyrics');
    
    if (!titolo) {
        lyricsDiv.innerHTML = '<span class="error">Inserisci almeno il titolo della canzone</span>';
        return;
    }

    lyricsDiv.textContent = 'Sto cercando il testo...';

    try {
        const response = await fetch('/get_lyrics', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                titolo: titolo,
                artista: artista || null
            })
        });

        const data = await response.json();

        if (data.success) {
            lyricsDiv.textContent = data.lyrics;
        } 
        else {
            lyricsDiv.innerHTML = `<span class="error">${data.error || 'Errore sconosciuto'}</span>`;
        }
    } 
    catch (error) {
        lyricsDiv.innerHTML = `<span class="error">Errore di connessione: ${error.message}</span>`;
    }
}