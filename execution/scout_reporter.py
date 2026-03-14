import pandas as pd
import json
import os
import matplotlib.pyplot as plt
import numpy as np

class ScoutReporter:
    def __init__(self, session_id):
        self.session_id = session_id
        self.output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "reports")
        self.charts_dir = os.path.join(self.output_dir, "charts")
        os.makedirs(self.charts_dir, exist_ok=True)

    def generate_json_payload(self, df: pd.DataFrame):
        """Produce l'estratto finale (JSON) pronto per il caricamento."""
        payload = df.to_dict(orient="records")
        report_data = {
            "session_id": self.session_id,
            "status": "APPROVED",
            "candidates_evaluated": len(df),
            "top_candidates": payload
        }
        file_path = os.path.join(self.output_dir, f"{self.session_id}_report.json")
        with open(file_path, "w") as f:
            json.dump(report_data, f, indent=4)
        print(f"    [Scout Reporter] ✅ JSON Report: {file_path}")
        return file_path

    def generate_radar_charts(self, df: pd.DataFrame, target_name: str, kpis: list):
        """Genera un grafico Radar (Spider Chart) confrontando il target con i Top 3."""
        print(f"    [Scout Reporter] Generazione Radar Charts...")
        
        # Filtra i top 3 simili (escluso il target se distanza=0)
        candidates = df[df['player_name'] != target_name].head(3)
        if candidates.empty:
            print("    [Scout Reporter] ⚠️ Nessun candidato trovato per il grafico.")
            return

        # Dati per il grafico
        labels = kpis
        num_vars = len(labels)
        angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
        angles += angles[:1] # Chiudi il cerchio

        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))

        def add_to_radar(name, color):
            row = df[df['player_name'] == name].iloc[0]
            values = [row[kpi] for kpi in kpis]
            # Normalizzazione veloce per il grafico (0-1)
            # In un sistema reale useremmo i valori dello scaler
            values = [(v / max(df[kpi])) if max(df[kpi]) != 0 else 0 for v, kpi in zip(values, kpis)]
            values += values[:1]
            ax.plot(angles, values, color=color, linewidth=2, label=name)
            ax.fill(angles, values, color=color, alpha=0.25)

        # Aggiungi Target
        if target_name in df['player_name'].values:
            add_to_radar(target_name, 'red')
        
        # Aggiungi Top Candidati
        colors = ['blue', 'green', 'orange']
        for i, (idx, row) in enumerate(candidates.iterrows()):
            add_to_radar(row['player_name'], colors[i])

        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)
        ax.set_thetagrids(np.degrees(angles[:-1]), labels)
        
        plt.title(f"Comparison: {target_name} vs Top Candidates", size=15, y=1.1)
        plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
        
        chart_path = os.path.join(self.charts_dir, f"{self.session_id}_radar.png")
        plt.savefig(chart_path, bbox_inches='tight')
        plt.close()
        
        print(f"    [Scout Reporter] ✅ Radar Chart salvato: {chart_path}")
        return chart_path
