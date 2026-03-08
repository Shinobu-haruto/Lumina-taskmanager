from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QMessageBox, QHBoxLayout
)
from PyQt6.QtCore import QTimer, Qt
import psutil

class ProcessTab(QWidget):
    def __init__(self, lang_data, parent=None):
        super().__init__(parent)
        self.lang_data = lang_data
        self.layout = QVBoxLayout(self)

        # Tabla de procesos
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            self.tr("proc_pid"), self.tr("proc_name"), 
            self.tr("proc_user"), self.tr("proc_status")
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.layout.addWidget(self.table)

        # Botón de acción
        button_container = QHBoxLayout()
        button_container.addStretch()
        self.action_button = QPushButton(self.tr("btn_action"))
        self.action_button.clicked.connect(self.perform_action)
        button_container.addWidget(self.action_button)
        self.layout.addLayout(button_container)

        # Actualización automática
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_processes)
        self.timer.start(3000)
        self.update_processes()

    def tr(self, key):
        """Traduce una clave usando el diccionario inyectado."""
        return self.lang_data.get(key, key)

    def update_processes(self):
        """Actualiza la lista de procesos en la tabla."""
        try:
            procs = list(psutil.process_iter(['pid', 'name', 'username', 'status']))
            self.table.setRowCount(0)
            for proc in procs:
                row = self.table.rowCount()
                self.table.insertRow(row)
                
                # Datos básicos
                self.table.setItem(row, 0, QTableWidgetItem(str(proc.info['pid'])))
                self.table.setItem(row, 1, QTableWidgetItem(proc.info['name'] or "N/A"))
                self.table.setItem(row, 2, QTableWidgetItem(proc.info['username'] or "N/A"))
                self.table.setItem(row, 3, QTableWidgetItem(proc.info['status']))

                # Colorear filas de sistema
                if self.is_system_process(proc):
                    for col in range(4):
                        item = self.table.item(row, col)
                        if item:
                            item.setBackground(Qt.GlobalColor.lightGray)
        except Exception as e:
            print(f"Error actualizando procesos: {e}")

    def get_selected_process(self):
        """Retorna el objeto psutil.Process de la fila seleccionada."""
        selected_rows = self.table.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            pid_item = self.table.item(row, 0)
            if pid_item:
                pid = int(pid_item.text())
                try:
                    return psutil.Process(pid)
                except psutil.NoSuchProcess:
                    QMessageBox.warning(self, self.tr("error_title"), self.tr("error_no_process"))
        return None

    def perform_action(self):
        """Decide si terminar o intentar reiniciar según el tipo de proceso."""
        proc = self.get_selected_process()
        if not proc:
            return
            
        if self.is_system_process(proc):
            self.restart_process(proc)
        else:
            self.terminate_process(proc)

    def is_system_process(self, proc):
        """Determina si un proceso es del sistema (por PID o nombre de usuario)."""
        try:
            uname = (proc.info.get('username') or "").lower()
            pid = proc.info.get('pid')
            return pid < 100 or 'root' in uname or 'system' in uname or 'local service' in uname
        except Exception:
            return True

    def terminate_process(self, proc):
        """Intenta finalizar un proceso de usuario."""
        try:
            proc.terminate()
        except Exception as e:
            QMessageBox.warning(self, self.tr("error_title"), f"{self.tr('error_terminate')}: {e}")

    def restart_process(self, proc):
        """Intenta reiniciar un proceso (simulado mediante terminación y espera)."""
        try:
            # En un administrador de tareas real, reiniciar es complejo. 
            # Aquí lo terminamos; si es un servicio de sistema, el SO suele relanzarlo.
            proc.terminate()
            proc.wait(timeout=3)
        except Exception as e:
            QMessageBox.warning(self, self.tr("error_title"), f"{self.tr('error_restart')}: {e}")
