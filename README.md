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

1. **Attiva l'ambiente virtuale**:
   ```bash
   source .venv/bin/activate
   ```
2. **Installa le dipendenze**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Inizializza il database**:
   ```bash
   python3 -m execution.setup_db
   ```
4. **Avvia lo scouting**:
   ```bash
   python3 -m execution.main_orchestrator
   ```

## 📁 Struttura Progetto
- `execution/`: Core logic (Harvester, Analysis, Reporting). Contiene `__init__.py` per permettere l'importazione come pacchetto.
- `history/`: Database SQLite dello storico scouting.
- `data/reports/`: Risultati generati (JSON e Grafici).
- `directives/`: Standard Operating Procedures (SOP).
