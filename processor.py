# processor.py
import pandas as pd
import numpy as np

class DataProcessor:
    def __init__(self):
        self.raw_data = None
        self.channels = []
        self.processed_data = None


    def load_csv(self, file_path):
        try:
            try:
                dframe = pd.read_csv(file_path, sep=';', decimal=',', engine='python', encoding='utf-8')
            except UnicodeDecodeError:
                try:
                    dframe = pd.read_csv(file_path, sep=';', decimal=',', engine='python', encoding='cp1250')
                except UnicodeDecodeError:
                    dframe = pd.read_csv(file_path, sep=';', decimal=',', engine='python', encoding='iso-8859-2')

            #usuń niepotrzebne kolumny
            unnecessary_cols = dframe.filter(regex='(?i)temperatura|nr').columns
            dframe = dframe.drop(columns=unnecessary_cols)
            dframe = dframe.iloc[1:].reset_index(drop=True)

            dframe['Czas [s]'] = dframe.index * 0.5            
            
            self.raw_data = dframe

            self.channels = [col for col in dframe.columns if any(s in col for s in ['N1', 'N2', 'N3', 'N4'])]
            if not self.channels:
                raise ValueError("Nie znaleziono kolumn z danymi przewodności (N1, N2, N3, N4).")
            
            return True, f"Pomyślnie wczytano plik: {file_path}"
        except Exception as e:
            return False, f"Błąd podczas wczytywania pliku: {str(e)}"
    
    def get_raw_plot_data(self, selected_channels):
        
        if self.raw_data is None:
            raise ValueError("Brak danych do przetworzenia. Wczytaj plik CSV.")
        
        valid_channels = [ch for ch in selected_channels if ch in self.raw_data.columns]
        
        x_data = self.raw_data['Czas [s]'].values.astype(float)
        y_data = {ch: self.raw_data[ch].values.astype(float) for ch in valid_channels}

        return x_data, y_data
        
    # Tutaj pojawią się funkcje do obliczania C_b i czasu mieszania
    def get_C_infinite(self, channel, x_pts = 0):
        if self.raw_data is None:
            raise ValueError("Brak danych do przetworzenia. Wczytaj plik CSV.")
        
        if channel not in self.raw_data.columns:
            raise ValueError(f"Nie znaleziono kanału: {channel}")
        #idiotoodporność
        try:
            x_pts = int(x_pts) if x_pts else 0
        except ValueError:
            x_pts = 0

        if x_pts > 0:
            x_pts = min(x_pts, len(self.raw_data))
            return self.raw_data[channel].iloc[:x_pts].mean()
        else:
            return self.raw_data[channel].iloc[-1]