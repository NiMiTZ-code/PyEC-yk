import sys
from PySide6.QtWidgets import QApplication
from gui import MainWindow

def main():
    app = QApplication(sys.argv)
    
    # Utworzenie i wyświetlenie głównego okna
    window = MainWindow()
    window.show()
    
    # Bezpieczne zamknięcie aplikacji
    sys.exit(app.exec())

if __name__ == "__main__":
    main()