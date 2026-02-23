import subprocess
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel,
    QListWidget, QHBoxLayout, QMessageBox
)
from PyQt6.QtCore import Qt

class RunProgramTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        # Título
        title = QLabel("New Task as Administrator")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.layout.addWidget(title)

        # Input y botón
        input_layout = QHBoxLayout()
        self.input_line = QLineEdit()
        self.input_line.setPlaceholderText("Execute Program")
        self.input_line.setStyleSheet("background-color: white; color: green; font-size: 14px;")
        input_layout.addWidget(self.input_line)

        self.run_button = QPushButton("Ejecutar")
        self.run_button.setStyleSheet("background-color: #f0f0f0; color: black;")
        self.run_button.clicked.connect(self.run_program)
        input_layout.addWidget(self.run_button)
        self.layout.addLayout(input_layout)

        # Historial
        self.layout.addWidget(QLabel("Historial:"))
        self.history_list = QListWidget()
        self.history_list.setStyleSheet("background-color: white; color: green;")
        self.history_list.itemDoubleClicked.connect(self.run_from_history)
        self.layout.addWidget(self.history_list)

        # Mensaje de estado
        self.status_label = QLabel("")
        self.layout.addWidget(self.status_label)

        # Lista interna para historial
        self.history = []

    def run_program(self):
        command = self.input_line.text().strip()
        if not command:
            QMessageBox.warning(self, "Error", "No se ha introducido ningún comando")
            return

        try:
            # Ejecutar el programa
            subprocess.Popen(command, shell=True)
            self.status_label.setText(f"Programa ejecutado: {command}")

            # Guardar en historial
            if command not in self.history:
                self.history.insert(0, command)
                self.history_list.insertItem(0, command)

            self.input_line.clear()
        except FileNotFoundError:
            QMessageBox.warning(self, "Error", f"No se encontró: {command}")
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def run_from_history(self, item):
        command = item.text()
        self.input_line.setText(command)
        self.run_program()
