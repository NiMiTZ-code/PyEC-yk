import re
import sys
import os
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTextBrowser, QStyle,
                               QPushButton, QLabel, QFileDialog, QGroupBox, QCheckBox, QLineEdit, QDialog)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QColor

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
        self.checkbox_dict = {}
        self.mix_time_results_lbls = {}

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
        self.layout_channel = QHBoxLayout()
        group_channel.setLayout(self.layout_channel)

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
        lbl_interval = QLabel("Przedział filtrowania (ilość punktów):")
        self.ibox_interval = QLineEdit()
        self.ibox_interval.setPlaceholderText("Wpisz wartość (np. 20)")
        self.ibox_interval.setText("1")  # Wpisujemy domyślną wartość na start!
        
        layout_interval.addWidget(lbl_interval)
        layout_interval.addWidget(self.ibox_interval)
        layout_res.addLayout(layout_interval)

        self.layout_res_lbls = QVBoxLayout()
        layout_res.addLayout(self.layout_res_lbls)

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

        #Export
        self.btn_export = QPushButton("Eksportuj wyniki do Excel")
        self.btn_export.clicked.connect(self.export_to_excel)
        group_export = QGroupBox("3. Export wyników")
        layout_export = QVBoxLayout()
        layout_export.addWidget(self.btn_export)
        group_export.setLayout(layout_export)
        

        #Help footer
        footer_layout = QHBoxLayout()
        self.btn_help = QPushButton(" Dokumentacja i Instrukcja Obsługi")
        self.btn_help.setIcon(self.style().standardIcon(QStyle.SP_MessageBoxQuestion))
        self.btn_help.clicked.connect(self.show_documentation)
        footer_layout.addWidget(self.btn_help)

        # Dodanie grup do lewego panelu
        control_panel.addWidget(group_file)
        control_panel.addWidget(group_calc)
        control_panel.addWidget(self.group_res)
        control_panel.addWidget(group_export)
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

        self.zoom = zoom_factory(self.ax_dimless)
        self.ph = panhandler(self.figure_dimless, button=2)
        self.dimless_cursor = None

        layout_plots.addWidget(self.canvas)
        layout_plots.addWidget(self.canvas_dimless)

        #SIGNALS
        self.btn_calculate.clicked.connect(self.on_plot_processed_clicked)
        self.btn_find_time.clicked.connect(self.on_find_time_clicked)

        # Złożenie całości (rozciągnięcie wykresu proporcją stretch)
        main_layout.addLayout(control_panel, stretch=1)
        main_layout.addLayout(layout_plots, stretch=3)
        self.load_stylesheet("style.qss")

    def load_stylesheet(self, path):
        with open(path, "r") as f:
            style = f.read()
            self.setStyleSheet(style)

    def load_file(self):
        # Okno dialogowe wyboru pliku
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Wybierz plik z danymi", "", "CSV Files (*.csv);;All Files (*)"
        )
        
        if file_path:
            success, message = self.processor.load_csv(file_path)
            
            if success:
                self.lbl_file_status.setText(f"Wczytany plik: {file_path.split('/')[-1]}")
                for i in reversed(range(self.layout_channel.count())):
                    self.layout_channel.itemAt(i).widget().setParent(None)
                self.checkbox_dict.clear()
                self.checked_channels.clear()

                for channel in self.processor.channels:
                    checkbox = QCheckBox(channel)
                    checkbox.toggled.connect(lambda checked, ch=channel: self.add_channel(checked, ch))
                    self.layout_channel.addWidget(checkbox)
                    self.checkbox_dict[channel] = checkbox
                
                #results labels
                for i in reversed(range(self.layout_res_lbls.count())):
                    self.layout_res_lbls.itemAt(i).widget().setParent(None)
                self.mix_time_results_lbls.clear()
                for channel in self.processor.channels:
                    lbl = QLabel(f"{channel}: -")
                    self.layout_res_lbls.addWidget(lbl)
                    self.mix_time_results_lbls[channel] = lbl
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
            if self.dimless_cursor is not None:
                self.dimless_cursor.remove()

            self.dimless_cursor = mplcursors.cursor(self.ax_dimless.get_lines(), hover=True)
            @self.dimless_cursor.connect("add")
            def on_add(sel):
                idx = int(round(sel.index))
                x_val, y_val = sel.artist.get_data()
                x_val = x_val[idx]
                y_val = y_val[idx]
                sel.annotation.xy = (x_val, y_val)
                sel.annotation.set_text(f"Czas: {x_val:.1f} s\nC_b: {y_val:.3f}")
                sel.annotation.get_bbox_patch().set(fc="white", alpha=0.9, edgecolor="black")
            
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
        if self.chbox_plot_limits.isChecked():
            self.chbox_plot_limits.setChecked(False)
        
    def on_find_time_clicked(self):

        interval_text = self.ibox_interval.text().strip()
        try:
            x_pts = int(interval_text) if interval_text else 1
        except ValueError:
            x_pts = 1
            self.ibox_interval.setText("1")

        mixing_times = self.processor.find_mixing_time(x_filtering_pts=x_pts)
        valid_times = [t for t in mixing_times.values() if t is not None]
        
        max_time = max(valid_times) if valid_times else None

        for ch, label in self.mix_time_results_lbls.items():
            label.setPalette(QPalette())
            label.setAutoFillBackground(False)
            if ch not in mixing_times:
                label.setText(f"{ch}: Brak danych")
            else:
                mt = mixing_times[ch]
                if mt is None:
                    label.setText(f"{ch}: Nie osiągnięto pełnego wymieszania")
                else:
                    label.setText(f"{ch}: {mt:.2f} s")
                    pallette = label.palette()
                    if len(valid_times) > 1:
                        if mt == max_time:
                            pallette.setColor(QPalette.Window, QColor(168,151,50))
                        
                        label.setPalette(pallette)
                        label.setAutoFillBackground(True)


        self.group_res.setVisible(True)
        print(mixing_times)

    def add_channel(self, checked, channel_name):
        if checked and channel_name not in self.checked_channels:
            self.checked_channels.append(channel_name)
        elif not checked and channel_name in self.checked_channels:
            self.checked_channels.remove(channel_name)

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

    def export_to_excel(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Zapisz plik Excel",
            "wyniki.xlsx",
            "Pliki Excel (*.xlsx)"
        )

        if not file_path:
            return

        success, message = self.processor.export_excel(file_path)