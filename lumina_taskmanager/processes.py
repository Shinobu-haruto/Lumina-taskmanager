from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QMessageBox, QHBoxLayout
)
from PyQt6.QtCore import QTimer, Qt
import psutil

class ProcessTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)

        # Tabla de procesos
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["PID", "Nombre", "Usuario", "Estado"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.layout.addWidget(self.table)

        # Contenedor inferior para el botón
        button_container = QHBoxLayout()
        button_container.addStretch()  # Empuja el botón a la derecha
        self.action_button = QPushButton("Finalizar / Reiniciar")
        self.action_button.clicked.connect(self.perform_action)
        button_container.addWidget(self.action_button)
        self.layout.addLayout(button_container)

        # Timer para actualizar la tabla
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_processes)
        self.timer.start(3000)

        self.update_processes()

    def update_processes(self):
        procs = list(psutil.process_iter(['pid', 'name', 'username', 'status']))
        self.table.setRowCount(0)
        for proc in procs:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(proc.info['pid'])))
            self.table.setItem(row, 1, QTableWidgetItem(proc.info['name']))
            self.table.setItem(row, 2, QTableWidgetItem(proc.info['username'] or "N/A"))
            self.table.setItem(row, 3, QTableWidgetItem(proc.info['status']))

            # Colorear filas de sistema
            if self.is_system_process(proc):
                for col in range(4):
                    item = self.table.item(row, col)
                    if item:
                        item.setBackground(Qt.GlobalColor.lightGray)

    def get_selected_process(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            pid_item = self.table.item(row, 0)
            if pid_item:
                pid = int(pid_item.text())
                try:
                    return psutil.Process(pid)
                except psutil.NoSuchProcess:
                    QMessageBox.warning(self, "Error", "El proceso ya no existe.")
        return None

    def perform_action(self):
        proc = self.get_selected_process()
        if not proc:
            return
        if self.is_system_process(proc):
            self.restart_process(proc)
        else:
            self.terminate_process(proc)

    def is_system_process(self, proc):
        try:
            uname = (proc.info['username'] or "").lower()
            return proc.info['pid'] < 100 or 'root' in uname or 'system' in uname
        except Exception:
            return True

    def terminate_process(self, proc):
        try:
            proc.terminate()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudo finalizar: {e}")

    def restart_process(self, proc):
        try:
            proc.terminate()
            proc.wait(timeout=3)
            # Aquí se puede reiniciar usando proc.exe() si es confiable
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudo reiniciar: {e}")
