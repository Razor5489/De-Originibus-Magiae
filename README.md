# De Originibus Magiae

Libro scolastico di **Storia della Magia**, autore fittizio **Theobald Ainsworth**, per Hogwarts nell’ambientazione 1890.

110 pagine A4 sfogliabili, nello stile della collana Ars Potium / Ars Incantationum. Sette annualità, ciascuna con due lezioni a settimana per due settimane: **28 incontri** complessivi.

Ogni incontro comprende tre pagine: spiegazione storica, nozioni centrali e confronto in aula con domanda e risposta ragionata. Sono incluse cronologia, lessico e nota sulle fonti.

## Programma

| Anno | Tema |
| --- | --- |
| I | Fondatori, comunità antiche, tracce e trasmissione del sapere |
| II | Merlino, Morgana, racconti, tradizioni e memoria pubblica |
| III | Maghi e Babbani, persecuzioni e Statuto di Segretezza |
| IV | Nascita del Ministero, Norwich, giustizia e libertà della bacchetta |
| V | Riforma Hawthorne, Preparazione Standard e cittadinanza |
| VI | Progresso, produzione e ricerca responsabile |
| VII | Fonti, laboratorio degli archivisti e Caso Wren |

Le prime due lezioni del primo anno conservano gli argomenti già documentati dalla scuola: I Quattro Fondatori e le comunità precedenti a Hogwarts.

## Fonti e criteri

Materiali forniti dall’utente: `Programma storia della magia.pdf` e `MANUALE DI SDM - BWGDR.pdf`. I PDF originali non vengono ripubblicati. I testi del libro sono una rielaborazione didattica.

Il programma specifico dell’ambientazione prevale sulla cronologia generica del manuale: Ministero britannico nel 1708, Riforma Hawthorne nel 1778, ingresso a sedici anni, Preparazione Standard teorica dagli undici ai quindici senza bacchetta né pratica volontaria. Gli eventi successivi al 1890 sono esclusi. I quattordici nuclei del programma sono sviluppati in ventotto incontri; il primo anno comprende anche approfondimenti antichi scelti dal manuale.

Gli esercizi documentali del 1732 e del 1874 sono esplicitamente immaginari e non aggiungono eventi ufficiali. La teoria di Wren rimane un’ipotesi e la scomparsa resta irrisolta. Per Norwich, Calderoni e Greywick non si aggiungono dettagli non documentati.

## Modifica e rigenerazione

- `content.json`: spiegazioni, nozioni, attività e ripasso delle 28 lezioni.
- `build-book.py`: genera le 110 pagine SVG, i dati del lettore e l’indice incorporato in `index.html`.
- `pages/`: pagine A4 statiche, già pronte per la pubblicazione.
- `reader.js`, `single-page-turn.js`, `reader-refinements.js`: lettore con una/due pagine, ricerca, ingrandimento e segnalibri locali.

Per ricostruire: Python 3 con `reportlab`, poi `python3 build-book.py`. La consultazione non richiede dipendenze o compilazione: GitHub Pages può pubblicare la cartella principale del ramo `main`.

Creato per NightFall da Razor. Progetto amatoriale non ufficiale.
