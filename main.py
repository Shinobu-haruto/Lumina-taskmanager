import sys
from PyQt6.QtWidgets import QApplication
from lumina_taskmanager.main_window import TaskManager

def main():
    app = QApplication(sys.argv)
    window = TaskManager()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
