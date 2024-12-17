import sys
from PySide6.QtWidgets import QApplication
from mainwindow import IDEMainWindow

def main():
    app = QApplication(sys.argv)
    window = IDEMainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
