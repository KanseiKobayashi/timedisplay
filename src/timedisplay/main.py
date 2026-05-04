import sys

from PySide6.QtWidgets import QApplication

from timedisplay.view import TimeDisplay

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TimeDisplay()
    window.show()
    sys.exit(app.exec())
