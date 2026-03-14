import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import euclidean_distances

class QuantAnalyst:
    def __init__(self, kpi_priority):
        """
        kpi_priority: dict con chiave = KPI e valore = peso (0-1)
        """
        self.kpi_priority = kpi_priority

    def process_data(self, df: pd.DataFrame, target_player_name: str = None, target_kpis: dict = None) -> pd.DataFrame:
        """
        1. Normalizza i dati.
        2. Identifica il vettore target (da df o da target_kpis).
        3. Calcola la distanza euclidea pesata.
        """
        if df.empty:
            print("    [Quant Analyst] ⚠️ DataFrame vuoto. Impossibile calcolare distanze.")
            return df

        features = list(self.kpi_priority.keys())
        valid_features = [f for f in features if f in df.columns]
        
        if not valid_features:
            print("    [Quant Analyst] ⚠️ Nessun KPI valido trovato nelle colonne del DataFrame.")
            return df

        # Normalizzazione
        scaler = MinMaxScaler()
        df_scaled = df.copy()
        df_scaled[valid_features] = scaler.fit_transform(df[valid_features])
        
        # Determinazione del vettore Target
        target_vector = None
        
        # Priorità 1: Target cercato nel pool corrente
        if target_player_name:
            target_row = df_scaled[df_scaled['player_name'] == target_player_name]
            if not target_row.empty:
                print(f"    [Quant Analyst] Target '{target_player_name}' trovato nel pool.")
                target_vector = target_row[valid_features].values
        
        # Priorità 2: Target passato come KPI manuali (es. da storico DB o inserimento manuale)
        if target_vector is None and target_kpis:
            print(f"    [Quant Analyst] Utilizzo KPI manuali/storici per il target.")
            # Dobbiamo creare un vettore normalizzato per il target kpis
            # Usiamo lo scaler già fittato sul pool corrente
            target_df = pd.DataFrame([target_kpis])
            # Assicurati che tutte le features siano presenti (anche se 0) per non rompere lo scaler
            for f in valid_features:
                if f not in target_df.columns:
                    target_df[f] = 0
            
            target_scaled = scaler.transform(target_df[valid_features])
            target_vector = target_scaled

        if target_vector is None:
            print("    [Quant Analyst] ⚠️ Impossibile determinare un vettore target. Calcolo distanza saltato.")
            df['similarity_score'] = 999.0
            return df

        # Calcolo Distanza Euclidea Pesata
        # Applichiamo i pesi
        weights = np.array([self.kpi_priority[f] for f in valid_features])
        
        candidate_vectors = df_scaled[valid_features].values
        
        # Distanza pesata per ogni riga
        weighted_diff = (candidate_vectors - target_vector) * weights
        distances = np.sqrt(np.sum(weighted_diff**2, axis=1))
        
        df['similarity_score'] = distances
        
        print(f"    [Quant Analyst] ✅ Distanze calcolate su {len(df)} candidati.")
        return df.sort_values(by='similarity_score')
