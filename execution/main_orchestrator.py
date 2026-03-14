import os
import sqlite3
from datetime import datetime
from pathlib import Path
import pandas as pd

from execution.harvester_agent import HarvesterAgent
from execution.quant_analyst import QuantAnalyst
from execution.scout_reporter import ScoutReporter

HISTORY_DB = Path(os.path.dirname(os.path.dirname(__file__))) / "history" / "scouting_archive.db"

class MainOrchestrator:
    def __init__(self):
        self.session_id = f"SESSION_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.harvester = HarvesterAgent()
        self.reporter = ScoutReporter(self.session_id)
        # Default Weights (can be made interactive or loaded from YAML)
        self.kpi_weights = {"xG90": 0.8, "ShotsOnTarget": 0.2, "goals_per_90": 0.5, "KeyPasses": 0.3}

    def start_interactive_session(self):
        print(f"\n{'='*50}")
        print(f"🚀 AUTO-SCOUT V1 - Statistica & Distanza")
        print(f"Session ID: {self.session_id}")
        print(f"{'='*50}\n")

        # 1. Ingestion File
        print("📁 [FOLDER SCAN] Inserisci i percorsi dei file CSV/Excel da analizzare (separati da virgola):")
        paths_raw = input(" > ").strip()
        file_paths = [p.strip() for p in paths_raw.split(",") if p.strip()]
        
        df = self.harvester.run_ingestion(file_paths)
        if df.empty:
            print("❌ Nessun dato caricato. Uscita.")
            return

        # 2. Scelta Target
        print(f"\n🔍 [TARGET] Chi è il giocatore di riferimento (Target)?")
        target_name = input(" Giocatore > ").strip()
        
        target_kpis = None
        # Verifica se è nel pool
        if target_name in df['player_name'].values:
            print(f"✅ '{target_name}' trovato nei file correnti.")
        else:
            # Verifica se è nel DB storico
            print(f"⚠️ '{target_name}' non trovato nei file. Cerco nel database storico...")
            target_kpis = self.harvester.get_player_history(target_name)
            
            if target_kpis:
                print(f"✅ '{target_name}' recuperato dalla memoria storica.")
            else:
                # Inserimento Manuale
                print(f"❓ '{target_name}' non trovato. Vuoi inserire i suoi KPI manualmente? (s/n)")
                if input(" > ").lower() == 's':
                    target_kpis = {}
                    print("Inserisci i valori per i seguenti KPI (invio per saltare/0):")
                    for kpi in self.kpi_weights.keys():
                        val = input(f" {kpi} > ").strip()
                        target_kpis[kpi] = float(val) if val else 0.0
                else:
                    print("❌ Impossibile procedere senza un profilo target.")
                    return

        # 3. Analisi Distanza
        quant = QuantAnalyst(self.kpi_weights)
        results_df = quant.process_data(df, target_player_name=target_name if not target_kpis else None, target_kpis=target_kpis)

        # 4. Show Results
        print(f"\n🏆 [RISULTATI] Top 5 Giocatori più simili a {target_name}:")
        top_5 = results_df.head(6) # Include il target stesso se presente
        # Escludi il target stesso dal display se la distanza è 0
        display_df = top_5[top_5['player_name'] != target_name].head(5)
        
        for i, (idx, row) in enumerate(display_df.iterrows(), 1):
            print(f" {i}. {row['player_name']} (Distanza: {row['similarity_score']:.4f})")

        # 5. Reporting & Visuals
        self.reporter.generate_json_payload(results_df)
        kpis_to_plot = list(self.kpi_weights.keys())
        self.reporter.generate_radar_charts(results_df, target_name, kpis_to_plot)
        
        print(f"\n✅ Sessione {self.session_id} completata con successo.")

if __name__ == "__main__":
    orchestrator = MainOrchestrator()
    orchestrator.start_interactive_session()
