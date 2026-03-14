import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'history', 'scouting_archive.db')

def setup_database():
    """Crea le tabelle SQLite se non esistono."""
    
    # Assicurati che la cartella 'history' esista
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Tabella Sessioni
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scouting_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE NOT NULL,
            target_profile TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            confidence_score REAL,
            execution_mode TEXT
        )
    ''')

    # Tabella Analisi Giocatori (Risultati delle sessioni)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS player_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            player_name TEXT NOT NULL,
            similarity_score REAL,
            confidence_score REAL,
            red_flags_found INTEGER DEFAULT 0,
            last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(session_id) REFERENCES scouting_sessions(session_id)
        )
    ''')

    # Tabella Storico KPI (La memoria del sistema)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historical_kpis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_name TEXT NOT NULL,
            kpi_name TEXT NOT NULL,
            kpi_value REAL NOT NULL,
            source TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(player_name, kpi_name) ON CONFLICT REPLACE
        )
    ''')

    conn.commit()
    conn.close()
    
    print(f"Database setup complete at: {DB_PATH}")

if __name__ == "__main__":
    setup_database()
