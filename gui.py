import sys
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QPushButton, QLabel, QFileDialog, QGroupBox)
from PySide6.QtCore import Qt

# Importy potrzebne do osadzenia Matplotlib w PySide6
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from processor import DataProcessor

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Analiza Krzywych Mieszania PK")
        self.resize(1000, 600)
        
        self.processor = DataProcessor()

        # Główny widget i layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # --- PANEL LEWY (Sterowanie) ---
        control_panel = QVBoxLayout()
        control_panel.setAlignment(Qt.AlignTop)
        
        # Sekcja Wczytywania
        group_file = QGroupBox("1. Operacje na plikach")
        layout_file = QVBoxLayout()
        self.btn_load = QPushButton("Wczytaj plik .csv")
        self.btn_load.clicked.connect(self.load_file)
        self.lbl_file_status = QLabel("Brak wczytanego pliku")
        layout_file.addWidget(self.btn_load)
        layout_file.addWidget(self.lbl_file_status)
        group_file.setLayout(layout_file)
        
        # Sekcja Obliczeń i Rysowania (przyciski na razie nieaktywne)
        group_calc = QGroupBox("2. Analiza i Wykresy")
        layout_calc = QVBoxLayout()
        self.btn_plot_raw = QPushButton("Rysuj wykres przewodności")
        self.btn_calculate = QPushButton("Przelicz (Stężenie bezwymiarowe)")
        self.btn_plot_limits = QPushButton("Dodaj granice 0.95 - 1.05")
        self.btn_find_time = QPushButton("Odczytaj czas mieszania")
        
        layout_calc.addWidget(self.btn_plot_raw)
        layout_calc.addWidget(self.btn_calculate)
        layout_calc.addWidget(self.btn_plot_limits)
        layout_calc.addWidget(self.btn_find_time)
        group_calc.setLayout(layout_calc)

        # Dodanie grup do lewego panelu
        control_panel.addWidget(group_file)
        control_panel.addWidget(group_calc)
        
        # --- PANEL PRAWY (Wykres Matplotlib) ---
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("Oczekuję na dane...")
        self.ax.set_xlabel("Czas, s")
        self.ax.set_ylabel("Przewodność / Stężenie")
        self.ax.grid(True)

        #SIGNALS
        self.btn_calculate.clicked.connect(self.on_plot_processed_clicked)
        self.btn_find_time.clicked.connect(self.on_find_time_clicked)
        # Złożenie całości (rozciągnięcie wykresu proporcją stretch)
        main_layout.addLayout(control_panel, stretch=1)
        main_layout.addWidget(self.canvas, stretch=3)

    def load_file(self):
        # Okno dialogowe wyboru pliku
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Wybierz plik z danymi", "", "CSV Files (*.csv);;All Files (*)"
        )
        
        if file_path:
            success, message = self.processor.load_csv(file_path)
            
            if success:
                self.lbl_file_status.setText(f"Wczytany plik: {file_path.split('/')[-1]}")
                
                x, y_data = self.processor.get_raw_plot_data(self.processor.channels)

                self.ax.clear()
                for channel_name, y_val in y_data.items():
                    self.ax.plot(x, y_val, label=channel_name)
                self.ax.set_title("Przewodność w funkcji czasu")
                self.ax.set_xlabel("Czas [s]")
                self.ax.set_ylabel("Przewodność [μS/cm]")
                self.ax.legend()
                self.ax.grid(True)
                self.canvas.draw()
            else:
                self.lbl_file_status.setText(message)

    def plot_processed_data(self):
        try:
            x, y_data = self.processor.get_processed_plot_data(self.processor.channels)

            self.ax.clear()
            for channel_name, y_val in y_data.items():
                self.ax.plot(x, y_val, label=channel_name)
            self.ax.set_title("Stężenie bezwymiarowe C_b w funkcji czasu")
            self.ax.set_xlabel("Czas [s]")
            self.ax.set_ylabel("Stężenie bezwymiarowe C_b")
            self.ax.legend()
            self.ax.grid(True)
            self.canvas.draw()
        except ValueError as e:
            self.lbl_file_status.setText(str(e))

    def on_plot_processed_clicked(self):
        self.plot_processed_data()
        
    def on_find_time_clicked(self):
        print(self.processor.find_mixing_time())