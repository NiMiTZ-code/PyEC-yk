import sys
import os
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTextBrowser, QStyle,
                               QPushButton, QLabel, QFileDialog, QGroupBox, QCheckBox, QLineEdit, QDialog)
from PySide6.QtCore import Qt

# Importy potrzebne do osadzenia Matplotlib w PySide6
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from mpl_interactions import zoom_factory, panhandler
import mplcursors

from processor import DataProcessor

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Analiza Krzywych Mieszania PK")
        self.resize(1000, 600)
        
        self.processor = DataProcessor()
        self.checked_channels = []

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

        #Sekcja wyboru kanałów
        group_channel = QGroupBox("Wybór kanałów")
        layout_channel = QHBoxLayout()
        self.chbox_channel_one = QCheckBox("Kanał 1")
        self.chbox_channel_two = QCheckBox("Kanał 2")
        self.chbox_channel_three = QCheckBox("Kanał 3")
        self.chbox_channel_four = QCheckBox("Kanał 4")
        self.chbox_channel_one.toggled.connect(lambda checked: self.add_channel(checked, "N1"))
        self.chbox_channel_two.toggled.connect(lambda checked: self.add_channel(checked, "N2"))
        self.chbox_channel_three.toggled.connect(lambda checked: self.add_channel(checked, "N3"))
        self.chbox_channel_four.toggled.connect(lambda checked: self.add_channel(checked, "N4"))
        self.chbox_channel_one.setEnabled(False)
        self.chbox_channel_two.setEnabled(False)
        self.chbox_channel_three.setEnabled(False)
        self.chbox_channel_four.setEnabled(False)

        layout_channel.addWidget(self.chbox_channel_one)
        layout_channel.addWidget(self.chbox_channel_two)
        layout_channel.addWidget(self.chbox_channel_three)
        layout_channel.addWidget(self.chbox_channel_four)
        group_channel.setLayout(layout_channel)

        #Sekcja ilości pomiarów
        group_meas_num= QGroupBox()
        layout_meas_num = QHBoxLayout()
        self.ibox_mes_num = QLineEdit()
        self.ibox_mes_num.setPlaceholderText("Wpisz wartość...")
        lbl_mes_num = QLabel("Ilość pomiarów:")
        
        layout_meas_num.addWidget(lbl_mes_num)
        layout_meas_num.addWidget(self.ibox_mes_num)
        group_meas_num.setLayout(layout_meas_num)

        #Sekcja wyników
        self.group_res = QGroupBox("3. Wyniki")
        layout_res = QVBoxLayout()

        layout_interval = QHBoxLayout()
        lbl_interval = QLabel("Przedzial o-o-b (ilość pkt przed):")
        self.ibox_interval = QLineEdit()
        self.ibox_interval.setPlaceholderText("Wpisz wartość (np. 20)")
        self.ibox_interval.setText("20")  # Wpisujemy domyślną wartość na start!
        
        layout_interval.addWidget(lbl_interval)
        layout_interval.addWidget(self.ibox_interval)

        self.lbl_ch_one_res = QLabel("Kanał 1: -")
        self.lbl_ch_two_res = QLabel("Kanał 2: -")
        self.lbl_ch_three_res = QLabel("Kanał 3: -")
        self.lbl_ch_four_res = QLabel("Kanał 4: -")
        
        layout_res.addLayout(layout_interval)

        layout_res.addWidget(self.lbl_ch_one_res)
        layout_res.addWidget(self.lbl_ch_two_res)
        layout_res.addWidget(self.lbl_ch_three_res)
        layout_res.addWidget(self.lbl_ch_four_res)
        self.group_res.setLayout(layout_res)
        self.group_res.setVisible(False)
        
        # Sekcja Obliczeń i Rysowania
        group_calc = QGroupBox("2. Analiza i Wykresy")
        layout_calc = QVBoxLayout()
        self.btn_plot_raw = QPushButton("Rysuj wykres przewodności")
        self.btn_plot_raw.clicked.connect(self.plot_data)
        self.btn_calculate = QPushButton("Przelicz i rysuj wykres (Stężenie bezwymiarowe)")
        self.chbox_plot_limits = QCheckBox("Dodaj granice 0.95 - 1.05")
        self.chbox_plot_limits.toggled.connect(self.on_plot_limits_toggled)
        self.btn_find_time = QPushButton("Odczytaj czas mieszania")
        
        layout_calc.addWidget(group_channel)
        layout_calc.addWidget(self.btn_plot_raw)
        layout_calc.addWidget(group_meas_num)
        layout_calc.addWidget(self.btn_calculate)
        layout_calc.addWidget(self.chbox_plot_limits)
        layout_calc.addWidget(self.btn_find_time)
        group_calc.setLayout(layout_calc)

        #Help footer
        footer_layout = QHBoxLayout()
        self.btn_help = QPushButton(" Dokumentacja i Instrukcja Obsługi")
        self.btn_help.setStyleSheet("""
            QPushButton {
                background-color: #4a5b6d;
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 4px;
                border: 1px solid #344352;
            }
            QPushButton:hover {
                background-color: #5c7085;
            }
            QPushButton:pressed {
                background-color: #344352;
            }
        """)
        self.btn_help.setIcon(self.style().standardIcon(QStyle.SP_MessageBoxQuestion))
        self.btn_help.clicked.connect(self.show_documentation)
        footer_layout.addWidget(self.btn_help)

        # Dodanie grup do lewego panelu
        control_panel.addWidget(group_file)
        control_panel.addWidget(group_calc)
        control_panel.addWidget(self.group_res)
        control_panel.addStretch()
        control_panel.addLayout(footer_layout)

        # --- PANEL PRAWY (Wykres Matplotlib) ---
        layout_plots = QVBoxLayout()

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("Oczekuję na dane...")
        self.ax.set_xlabel("Czas, s")
        self.ax.set_ylabel("Przewodność / Stężenie")
        self.ax.grid(True)

        self.figure_dimless = Figure()
        self.canvas_dimless = FigureCanvas(self.figure_dimless)
        self.ax_dimless = self.figure_dimless.add_subplot(111)
        self.ax_dimless.set_title("Oczekuję na dane...")
        self.ax_dimless.set_xlabel("Czas, s")
        self.ax_dimless.set_ylabel("Stężenie bezwymiarowe C_b")
        self.ax_dimless.grid(True)

        layout_plots.addWidget(self.canvas)
        layout_plots.addWidget(self.canvas_dimless)

        #SIGNALS
        self.btn_calculate.clicked.connect(self.on_plot_processed_clicked)
        self.btn_find_time.clicked.connect(self.on_find_time_clicked)

        # Złożenie całości (rozciągnięcie wykresu proporcją stretch)
        main_layout.addLayout(control_panel, stretch=1)
        main_layout.addLayout(layout_plots, stretch=3)

    def load_file(self):
        # Okno dialogowe wyboru pliku
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Wybierz plik z danymi", "", "CSV Files (*.csv);;All Files (*)"
        )
        
        if file_path:
            success, message = self.processor.load_csv(file_path)
            
            if success:
                self.lbl_file_status.setText(f"Wczytany plik: {file_path.split('/')[-1]}")
                self.chbox_channel_one.setEnabled(True)
                self.chbox_channel_two.setEnabled(True)
                self.chbox_channel_three.setEnabled(True)
                self.chbox_channel_four.setEnabled(True)
            else:
                self.lbl_file_status.setText(message)

    def plot_data(self):
        try:
            x, y_data = self.processor.get_raw_plot_data(self.checked_channels)
            self.ax.clear()
            for channel_name, y_val in y_data.items():
                self.ax.plot(x, y_val, label=channel_name)
            self.ax.set_title("Przewodność w funkcji czasu")
            self.ax.set_xlabel("Czas [s]")
            self.ax.set_ylabel("Przewodność [μS/cm]")
            self.ax.legend()
            self.ax.grid(True)
            self.canvas.draw()
        except ValueError as e:
            self.lbl_file_status.setText(str(e))

    def plot_processed_data(self, x_pts):
        try:
            x, y_data = self.processor.get_processed_plot_data(self.checked_channels, x_pts)

            self.ax_dimless.clear()
            for channel_name, y_val in y_data.items():
                self.ax_dimless.plot(x, y_val, label=channel_name)
            self.ax_dimless.set_title("Stężenie bezwymiarowe C_b w funkcji czasu")
            self.ax_dimless.set_xlabel("Czas [s]")
            self.ax_dimless.set_ylabel("Stężenie bezwymiarowe C_b")
            self.ax_dimless.legend()
            self.ax_dimless.grid(True)

            cursor = mplcursors.cursor(self.ax_dimless.get_lines(), hover=True)
            @cursor.connect("add")
            def on_add(sel):
                idx = int(round(sel.index))
                x_val, y_val = sel.artist.get_data()
                x_val = x_val[idx]
                y_val = y_val[idx]
                sel.annotation.xy = (x_val, y_val)
                sel.annotation.set_text(f"Czas: {x_val:.1f} s\nC_b: {y_val:.3f}")
                sel.annotation.get_bbox_patch().set(fc="white", alpha=0.9, edgecolor="black")

            self.zoom = zoom_factory(self.ax_dimless)
            self.ph = panhandler(self.figure_dimless, button=2)
            
            self.canvas_dimless.draw()

        except ValueError as e:
            self.lbl_file_status.setText(str(e))

    def on_plot_limits_toggled(self, checked):
        if checked:
            self.ax_dimless.axhline(0.95, color='red', linestyle='--')
            self.ax_dimless.axhline(1.05, color='red', linestyle='--')
        else:
            lines = self.ax_dimless.get_lines()
            for line in lines:
                if line.get_label() in ['Granica 0.95', 'Granica 1.05']:
                    line.remove()
        self.canvas_dimless.draw()

    def on_plot_processed_clicked(self):
        mes_num = self.ibox_mes_num.text().strip()

        try:
            x_pts = int(mes_num) if mes_num else 0
        except ValueError:
            self.lbl_file_status.setText("Nieprawidłowa ilość pomiarów. Używam domyślnej wartości.")
            return
        
        self.plot_processed_data(x_pts)
        
    def on_find_time_clicked(self):

        interval_text = self.ibox_interval.text().strip()
        try:
            x_pts = int(interval_text) if interval_text else 1
        except ValueError:
            x_pts = 1
            self.ibox_interval.setText("1")

        mixing_times = self.processor.find_mixing_time(x_filtering_pts=x_pts)
        label_map = {
            next((c for c in self.processor.channels if "N1" in c), None): self.lbl_ch_one_res,
            next((c for c in self.processor.channels if "N2" in c), None): self.lbl_ch_two_res,
            next((c for c in self.processor.channels if "N3" in c), None): self.lbl_ch_three_res,
            next((c for c in self.processor.channels if "N4" in c), None): self.lbl_ch_four_res,
        }
        for ch, label in label_map.items():
            if ch not in mixing_times:
                label.setText(f"{ch}: brak danych")
            else:
                t = mixing_times[ch]
            if t is None:
                label.setText(f"{ch}: nie osiągnięto zakresu")
            else:
                label.setText(f"{ch}: {t:.2f} s")

        self.group_res.setVisible(True)
        print(mixing_times)

    def add_channel(self, checked, channel_name):
        full_name = next((c for c in self.processor.channels if channel_name in c), None)

        if not full_name:
            self.lbl_file_status.setText(f"Nie znaleziono kanału zawierającego: {channel_name}")
            return
        
        if checked:
            if full_name not in self.checked_channels:
                self.checked_channels.append(full_name)
        else:
            if full_name in self.checked_channels:
                self.checked_channels.remove(full_name)

    def show_documentation(self):
        self.help_dialog = QDialog(self)
        self.help_dialog.setWindowTitle("Dokumentacja | Instrukcja obsługi")
        self.help_dialog.resize(650, 600)

        layout = QVBoxLayout(self.help_dialog)

        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        doc_path = os.path.join(os.path.dirname(__file__), "docs", "docs.html")

        try:
            with open(doc_path, 'r', encoding='utf-8') as file:
                html_content = file.read()
                browser.setHtml(html_content)
        except FileNotFoundError:
            browser.setHtml("<h2 style='color:red;'>Błąd 404</h2><p>Nie znaleziono pliku <b>docs.html</b> w folderze z aplikacją.</p>")
        except Exception as e:
            browser.setHtml(f"<h2 style='color:red;'>Błąd odczytu</h2><p>{str(e)}</p>")
        layout.addWidget(browser)
        self.help_dialog.show()
