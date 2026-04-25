# processor.py
import pandas as pd

class DataProcessor:
    def __init__(self):
        self.raw_data = None
        self.channels = []
        self.processed_data = None


    def load_csv(self, file_path):
        try:
            dframe = pd.read_csv(file_path, sep=';', engine='python')
            #usuń niepotrzebne kolumny
            unnecessary_cols = dframe.filter(like='Temperatura').columns
            dframe = dframe.drop(columns=unnecessary_cols)
            dframe = dframe.iloc[1:].reset_index(drop=True)
            self.raw_data = dframe

            self.channels = [col for col in dframe.columns if any(s in col for s in ['N1', 'N2', 'N3', 'N4'])]
            if not self.channels:
                raise ValueError("Nie znaleziono kolumn z danymi przewodności (N1, N2, N3, N4).")
            
            return True, f"Pomyślnie wczytano plik: {file_path}"
        except Exception as e:
            return False, f"Błąd podczas wczytywania pliku: {str(e)}"
        
    # Tutaj pojawią się funkcje do obliczania C_b i czasu mieszania