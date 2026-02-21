import psutil

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout,
    QTableWidget, QTableWidgetItem,
    QPushButton, QMessageBox
)
from PyQt6.QtCore import QTimer


class ProcessTab(QWidget):

    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout(self)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(
            ["PID", "Nombre", "CPU %", "Memoria %"]
        )
        self.layout.addWidget(self.table)

        self.kill_button = QPushButton("Finalizar proceso")
        self.kill_button.clicked.connect(self.kill_selected_process)
        self.layout.addWidget(self.kill_button)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_processes)
        self.timer.start(2000)

        self.update_processes()

    def update_processes(self):

        processes = list(
            psutil.process_iter(
                ['pid', 'name', 'cpu_percent', 'memory_percent']
            )
        )

        self.table.setRowCount(len(processes))

        for row, process in enumerate(processes):

            self.table.setItem(
                row, 0,
                QTableWidgetItem(str(process.info['pid']))
            )
            self.table.setItem(
                row, 1,
                QTableWidgetItem(str(process.info['name']))
            )
            self.table.setItem(
                row, 2,
                QTableWidgetItem(str(process.info['cpu_percent']))
            )
            self.table.setItem(
                row, 3,
                QTableWidgetItem(
                    f"{process.info['memory_percent']:.2f}"
                )
            )

    def kill_selected_process(self):

        selected = self.table.currentRow()
        if selected < 0:
            return

        pid = int(self.table.item(selected, 0).text())
        name = self.table.item(selected, 1).text()

        reply = QMessageBox.question(
            self,
            "Confirmar",
            f"¿Finalizar proceso '{name}' (PID {pid})?",
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                proc = psutil.Process(pid)
                proc.terminate()
                proc.wait(timeout=3)
            except Exception:
                pass

        self.update_processes()

    def stop(self):
        self.timer.stop()
