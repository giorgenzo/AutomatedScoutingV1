# 🚀 AutomatedScoutingV1 - Scouting Calculator

Sistema interattivo per lo scouting calcistico basato su analisi statistica di prossimità (Euclidean Distance) e persistenza dei dati locale.

## 📌 Funzionamento
Il sistema permette di caricare file CSV/Excel contenenti statistiche dei giocatori e di confrontarli con un "Target Player" per trovare profili tecnicamente simili.

### Caratteristiche Principali:
- **Interactive CLI**: Modalità "Stop-and-Ask" per guidare l'utente nell'ingestion e nella scelta del target.
- **Distance Engine**: Calcolo della distanza euclidea pesata basata su KPI personalizzabili (xG90, Passaggi Chiave, etc.).
- **Data Persistence**: Salvataggio storico dei giocatori in SQLite. Il sistema "ricorda" i KPI dei giocatori importati in precedenza.
- **Manual Target Entry**: Possibilità di inserire manualmente i KPI di un giocatore target se non presente nel database.
- **Visual Reporting**: Generazione di Radar Charts (Spider Charts) per il confronto visivo tra il Target e i Top 3 candidati.

## 🛠️ Requisiti
- Python 3.8+
- Dipendenze: `pandas`, `numpy`, `scikit-learn`, `matplotlib`, `openpyxl`

## 🚀 Utilizzo
1. Installa le dipendenze: `pip install -r requirements.txt` (Assicurati che pandas e sklearn siano installati)
2. Inizializza il database: `python3 execution/setup_db.py`
3. Avvia lo scouting: `python3 execution/main_orchestrator.py`

## 📁 Struttura Progetto
- `execution/`: Core logic (Harvester, Analysis, Reporting).
- `history/`: Database SQLite dello storico scouting.
- `data/reports/`: Risultati generati (JSON e Grafici).
- `directives/`: Standard Operating Procedures (SOP).
