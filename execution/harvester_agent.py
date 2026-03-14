import pandas as pd
import os
import sqlite3
from datetime import datetime

class HarvesterAgent:
    def __init__(self, data_sources=None):
        self.data_sources = data_sources or {}
        self.internal_db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "history", "scouting_archive.db")

    def run_ingestion(self, file_paths=None) -> pd.DataFrame:
        """
        Legge i file (CSV/Excel) e restituisce un DataFrame normalizzato.
        Salva anche i dati nel DB storico.
        """
        all_dfs = []
        files = file_paths or self.data_sources.get("local_files", [])
        
        for file in files:
            if not os.path.exists(file):
                print(f"    [Harvester] ⚠️ File non trovato: {file}")
                continue
                
            try:
                if file.endswith('.csv'):
                    df = pd.read_csv(file)
                elif file.endswith(('.xlsx', '.xls')):
                    df = pd.read_excel(file)
                else:
                    print(f"    [Harvester] ⚠️ Formato file non supportato: {file}")
                    continue
                
                print(f"    [Harvester] Caricato {file} con {len(df)} righe.")
                df['source_file'] = os.path.basename(file)
                all_dfs.append(df)
                
                # Persistenza automatica
                self.store_historical_data(df, source=file)
                
            except Exception as e:
                print(f"    [Harvester] ❌ Errore durante la lettura di {file}: {e}")

        if not all_dfs:
            return pd.DataFrame()
            
        return pd.concat(all_dfs, ignore_index=True)

    def store_historical_data(self, df: pd.DataFrame, source="manual"):
        """Salva i KPI dei giocatori nel database storico."""
        conn = sqlite3.connect(self.internal_db_path)
        cursor = conn.cursor()
        
        # Identifica colonne KPI (tutte tranne nomi e metadati)
        metadata_cols = ['player_name', 'name', 'source_file', 'timestamp', 'id']
        kpi_cols = [c for c in df.columns if c.lower() not in metadata_cols]
        
        name_col = 'player_name' if 'player_name' in df.columns else ('name' if 'name' in df.columns else None)
        
        if not name_col:
            print("    [Harvester] ⚠️ Impossibile salvare: Colonna 'player_name' mancante.")
            return

        for _, row in df.iterrows():
            player_name = row[name_col]
            for kpi in kpi_cols:
                try:
                    val = float(row[kpi])
                    cursor.execute('''
                        INSERT INTO historical_kpis (player_name, kpi_name, kpi_value, source)
                        VALUES (?, ?, ?, ?)
                        ON CONFLICT(player_name, kpi_name) DO UPDATE SET
                        kpi_value = excluded.kpi_value,
                        source = excluded.source,
                        timestamp = CURRENT_TIMESTAMP
                    ''', (player_name, kpi, val, source))
                except (ValueError, TypeError):
                    continue # Salta dati non numerici per i KPI
        
        conn.commit()
        conn.close()

    def get_player_history(self, player_name: str) -> dict:
        """Recupera i KPI storici di un giocatore dal DB."""
        conn = sqlite3.connect(self.internal_db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT kpi_name, kpi_value FROM historical_kpis WHERE player_name = ?", (player_name,))
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return None
            
        return {row['kpi_name']: row['kpi_value'] for row in rows}
