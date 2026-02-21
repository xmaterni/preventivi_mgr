# SPECIFICHE TECNICHE - PREVENTIVI MANAGER v1.5
Documento di Riferimento Architetturale

Questo documento stabilisce le linee guida tecniche e i principi fondamentali dell'applicativo `preventivi_mgr`. Ogni futura modifica **DEVE** aderire a questi standard.

## 1. Architettura Modulare (Standalone)

L'applicazione è progettata per essere un'entità autonoma. Le dipendenze esterne sono ridotte alla Standard Library di Python e alla libreria `tkinter`.

- **`data_engine.py` (Persistent Layer)**: 
    - Gestisce SQLite.
    - Implementa modelli dati: `PriceItem`, `QuoteHeader`, `QuoteLineItem`.
    - **Import CSV**: Utilizza `csv.reader` su indici di colonna fissi per ignorare header complessi/multi-riga.
    - **Snapshot Pricing**: Le righe preventivo contengono una copia del prezzo e della descrizione della voce del prezzario al momento dell'aggiunta.
- **`gui_config.py` (Styling Layer)**: 
    - Contiene le costanti `COLOR_*`, `FONT_*`.
    - Centralizza lo stile dei widget `Entry`, `Button`, `Treeview`.
- **`preventivi_mgr.py` (App Layer)**: 
    - Orchestrazione GUI (Tkinter/TTK).
    - Implementa ordinamento `Treeview` dinamico (Stringhe vs Numeri).
    - Gestisce i dialoghi di conferma colorati personalizzati.
    - Include un navigatore file interno (`_custom_file_browser`) per evitare campi di testo superflui.

## 2. Modello Dati (SQLite)

- `price_list`: `id`, `code` (unique), `description`, `unit`, `price` (real), `category`.
- `quotes`: `id`, `customer_name`, `date_created`, `total_amount`, `notes`.
- `quote_items`: `id`, `quote_id`, `item_code`, `description`, `quantity`, `unit_price`, `total_price`, `unit`.

## 3. Standard di Codifica (Binder)

- **Return Strict**: Vietato `return func()`. Obbligatorio `res = func(); return res`.
- **Fail Fast**: Validazione `if not data: return`.
- **Lingua**: Commenti/Docstring in **Italiano**, Simboli/Codice in **Inglese**.
- **UI Consistency**: 
    - Tutti i pulsanti di gestione (NUOVO, SALVA, IMPORTA, ELIMINA) devono usare lo stesso `get_button_style()`.
    - La barra superiore (Header) deve contenere esclusivamente azioni di sistema (HELP, ESCI).
    - La barra inferiore (Status Bar) deve mostrare lo stato del database.

## 4. Logica delle Conferme

Tutte le azioni distruttive o di ricalcolo massivo richiedono l'invocazione di `_custom_confirm` che garantisce:
- Titolo e Messaggio chiari.
- Pulsante **SÌ (VERDE, #008800)** a sinistra.
- Pulsante **NO (ROSSO, #AA0000)** a destra.
- Blocco dell'interfaccia (Transient/Grab) fino a risposta.

## 5. Navigazione File

Il selettore file (`_custom_file_browser`) deve essere implementato senza widget `Entry` per il nome file. La selezione avviene tramite `Listbox` navigabile (Double-click per DIR, Single-click + Button per FILE).

======================================================================
Fine Documento Specifiche.
