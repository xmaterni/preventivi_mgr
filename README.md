# GESTIONALE PREVENTIVI EDILE (Standalone)
Versione 1.5.0 - "Geometra Digitale"

Questo applicativo è uno strumento **professionale, autonomo e portatile** progettato per la gestione rapida di prezzari e la generazione di preventivi edili. Segue una filosofia di design rigorosa, focalizzata sulla produttività e sulla riduzione di input superflui.

## 🚀 Avvio Rapido

L'applicazione è contenuta interamente nella cartella `prv/`. Per avviarla:

1. Apri un terminale nella cartella `prv/`.
2. Esegui:
   ```bash
   python3 preventivi_mgr.py
   ```

## 🛠 Struttura del Pacchetto

La cartella è organizzata in modo da essere completamente isolata dal resto del sistema:

- **`preventivi_mgr.py`**: Punto di ingresso dell'applicazione (Interfaccia GUI).
- **`data_engine.py`**: Motore logico e persistenza dati (SQLite).
- **`gui_config.py`**: Configurazioni estetiche (Colori, Font, Stili).
- **`data/`**: Contiene il database SQLite `computa_ai.db`.
- **`imports/`**: Cartella suggerita per i listini CSV sorgente.
- **`exports/`**: Destinazione automatica dei preventivi generati in formato `.txt`.

## 📋 Funzionalità Chiave

- **Gestione Prezzario**:
    - Importazione CSV intelligente tramite selettore file navigabile (senza campi di testo ridondanti).
    - Ordinamento istantaneo cliccando sulle intestazioni delle colonne.
    - Scrollbar orizzontali e verticali per consultare descrizioni tecniche lunghe.
    - Azioni separate per singola riga (Salva/Elimina) e per intera tabella (Importa/Cancella).
- **Gestione Preventivi**:
    - Creazione testate preventivo per cliente.
    - Selezione voci dal prezzario con inserimento quantità.
    - **Snapshot Prezzi**: Il prezzo viene congelato nel preventivo; modifiche al listino master non alterano i lavori già preventivati.
    - Esportazione professionale in formato testuale pronto per la consegna.
- **Interfaccia "Geometra Dark"**:
    - Tema ad alto contrasto per ridurre l'affaticamento visivo.
    - Dialoghi di conferma con pulsanti **SÌ (VERDE)** e **NO (ROSSO)**.
    - Pulsanti di navigazione ed uscita rapidi nell'header.

## 📝 Note per lo Sviluppo
Il codice segue rigorosamente le Best Practices del progetto:
- Nomi di variabili e funzioni in **Inglese**.
- Commenti e documentazione in **Italiano**.
- Regola **Return Strict**: ogni risultato è assegnato a una variabile prima del ritorno.
- Logica **Fail Fast**: validazione immediata degli input.
