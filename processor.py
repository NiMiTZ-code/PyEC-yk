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

    def get_processed_plot_data(self, selected_channels):
        
        self.process_data()

        if self.processed_data is None:
            raise ValueError("Brak przetworzonych danych do wyświetlenia. Najpierw oblicz C_b.")
        
        valid_channels = [ch for ch in selected_channels if ch in self.processed_data.columns]
        
        x_data = self.processed_data['Czas [s]'].values.astype(float)
        y_data = {ch: self.processed_data[ch].values.astype(float) for ch in valid_channels}

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
        
    def calculate_C_b(self, c_infinite_dict):
        #c_infinite_dict to słownik z kluczami jako nazwy kanałów i wartościami jako C_infinite dla tych kanałów
        if self.raw_data is None:
            raise ValueError("Brak danych do przetworzenia. Wczytaj plik CSV.")
        
        self.processed_data = self.raw_data[['Czas [s]']].copy()

        for channel in self.channels:
            if channel in c_infinite_dict:
                c_infinite = c_infinite_dict[channel]
                c_0 = self.raw_data[channel].iloc[0]

                if c_infinite == c_0:
                    self.processed_data[channel] = 0.0
                else:
                    self.processed_data[channel] = (self.raw_data[channel] - c_0) / (c_infinite - c_0)

        return True, "Pomyślnie obliczono stężenie bezwymiarowe C_b dla dostępnych kanałów."
    
    def process_data(self):
        if self.raw_data is None:
            raise ValueError("Brak danych do przetworzenia. Wczytaj plik CSV.")
        
        c_infinite_dict = {channel: self.get_C_infinite(channel) for channel in self.channels}
        return self.calculate_C_b(c_infinite_dict)

    def find_mixing_time(self, lower_bound=0.95, upper_bound=1.05):
        if self.processed_data is None:
            raise ValueError("Brak przetworzonych danych. Najpierw oblicz C_b.")
        
        mixing_times = {}

        for channel in self.channels:
            if channel not in self.processed_data.columns:
                continue
            c_b_values = self.processed_data[channel].values
            time_values = self.processed_data['Czas [s]'].values

            #wektoryzowanie w NumPy jest ok dla bardzo duzej ilosci punktow danych
            #u nas nie ma różnicy w szybkości, więc proste poszukiwanie

            mixed_time = None
            if not (lower_bound <= c_b_values[-1] <= upper_bound):
                mixing_times[channel] = None
                continue

            for i in range(len(c_b_values) -1, -1, -1):
                if not (lower_bound <= c_b_values[i] <= upper_bound):
                    mixed_time = time_values[i+1]
                    break
            
            if mixed_time is None:
                mixed_time = time_values[0]

            mixing_times[channel] = mixed_time
        
        return mixing_times
    


     