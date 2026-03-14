# STANDARD OPERATING PROCEDURE (SOP): Universal Data Ingestion & Resilience

## 1. Obiettivo dell'Ingestion Layer
Il sottosistema di ingestione, gestito dall'agente **The Harvester**, ha lo scopo di raccogliere, mappare, e normalizzare dati da diverse sorgenti eterogenee.
Le sorgenti ammesse includono:
- **API Online**: Fotmob, Understat, Transfermarkt.
- **File Locali Eterogenei**: Estrazioni Wyscout in `.csv` o `.xlsx`, dump personalizzati in `.json`.

Indipendentemente dalla provenienza, le informazioni grezze devono essere uniformate in un modello interno basato su formato `Parquet` memorizzato nella cartella `/data/`.

# SOP: Ingestione e Persistenza Locale

## 1. Obiettivo
Garantire che ogni dato importato via CSV/Excel venga memorizzato permanentemente nel database `scouting_archive.db` per consentire ricerche future senza dover ricaricare i file.

## 2. Processo di Ingestione
1. **Scansione File**: L'utente fornisce i percorsi dei file.
2. **Normalizzazione**: I KPI vengono convertiti in valori numerici Float.
3. **Persistenza (UPSERT)**: Se un giocatore esiste già nel DB, i suoi KPI vengono aggiornati; altrimenti viene creata una nuova voce.

## 3. Gestione del Target
- Se il giocatore target è nel pool corrente (file appena caricati), i dati vengono presi da lì.
- Se non è nel pool, il sistema interroga il database storico.
- Se non è nel database, viene richiesto l'inserimento manuale via CLI.
- **Priorità 1 - Proxy Metrics**: Se un KPI strategico è nullo, l'agente deve calcolarlo utilizzando proxy disponibili prima di tentare l'imputazione.
  - *Esempio 1*: Se manca `xA` (Expected Assists), usa `Proxy_xA = (Key_Passes * 0.5) + Assists`.
  - *Esempio 2*: Se manca `xG_Buildup`, usa i possessi recuperati nel terzo finale.
- **Priorità 2 - Imputazione via Mediana di Ruolo**: Se il proxy non è applicabile, il dato mancante viene rimpiazzato con la **mediana dei giocatori con lo stesso ruolo** (`player_position`). 
  - *Evitare medie matematiche* (Mean) che potrebbero sbilanciare i percentili a causa di outlier. Altrimenti usare Zero.

## 4. Logica di Lazy Update (TTL Caching)
Il sistema è orientato al contenimento delle risorse (rate-limits o limitazioni di budget API) e usa una logica ibrida e "pigra":
- Quando `execution_mode: "hybrid"` è attivo nel file di configurazione YAML, **The Harvester** verifica innanzitutto se il file `/data/internal_model.parquet` esiste.
- Se la data di ultima modifica di quel file è **più vecchia di 7 giorni** (Auto-Update TTL), l'agente avvia il download dei nuovi raw-data online.
- Se il file ha un'età inferiore a 7 giorni, il sistema evita ogni chiamata API e processa la risorsa locale esistente garantendo alta responsività.
