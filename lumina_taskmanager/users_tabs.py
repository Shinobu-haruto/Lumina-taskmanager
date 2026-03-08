from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem
from PyQt6.QtCore import QTimer, Qt
import psutil
import datetime

class UsersTab(QWidget):
    def __init__(self, lang_data, parent=None):
        # 1. Iniciamos el QWidget con el padre
        super().__init__(parent)
        
        # 2. Guardamos el diccionario de idiomas PRIMERO
        self.lang_data = lang_data
        
        # 3. Configuramos el Layout
        self.layout = QVBoxLayout(self)
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        
        # 4. Ahora sí podemos poner los encabezados usando self.lang_data
        self.set_headers()
        
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft)
        self.table.setAlternatingRowColors(True)
        self.layout.addWidget(self.table)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_users)
        self.timer.start(5000)

        self.update_users()

    def tr(self, key):
        """Método local para traducir usando el diccionario inyectado."""
        return self.lang_data.get(key, key)

    def set_headers(self):
        """Asigna los encabezados usando el diccionario local."""
        self.table.setHorizontalHeaderLabels([
            self.tr("user_header"), 
            self.tr("terminal_header"), 
            self.tr("host_header"), 
            self.tr("login_header"), 
            self.tr("duration_header")
        ])

    def update_users(self):
        users = psutil.users()
        self.table.setRowCount(len(users))
        now = datetime.datetime.now()

        for row, user in enumerate(users):
            login_time = datetime.datetime.fromtimestamp(user.started)
            login_str = login_time.strftime("%H:%M:%S")
            session_duration = now - login_time
            hours, remainder = divmod(session_duration.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            duration_str = f"{hours}h {minutes}m"

            self.table.setItem(row, 0, QTableWidgetItem(user.name))
            self.table.setItem(row, 1, QTableWidgetItem(str(user.terminal or "N/A")))
            self.table.setItem(row, 2, QTableWidgetItem(str(user.host or "N/A")))
            self.table.setItem(row, 3, QTableWidgetItem(login_str))
            self.table.setItem(row, 4, QTableWidgetItem(duration_str))

            for col in range(5):
                item = self.table.item(row, col)
                if item:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
