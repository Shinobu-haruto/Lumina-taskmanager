from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem
from PyQt6.QtCore import QTimer, Qt
import psutil
import datetime

class UsersTab(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout(self)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["Usuario", "Terminal", "Host", "Login", "Tiempo conectado"]
        )
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft)
        self.table.setAlternatingRowColors(True)
        self.layout.addWidget(self.table)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_users)
        self.timer.start(5000)

        self.update_users()

    def update_users(self):
        users = psutil.users()
        self.table.setRowCount(len(users))

        now = datetime.datetime.now()

        for row, user in enumerate(users):
            login_time = datetime.datetime.fromtimestamp(user.started)
            login_str = login_time.strftime("%H:%M:%S")
            session_duration = now - login_time
            hours, remainder = divmod(session_duration.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            duration_str = f"{hours}h {minutes}m"

            self.table.setItem(row, 0, QTableWidgetItem(user.name))
            self.table.setItem(row, 1, QTableWidgetItem(str(user.terminal)))
            self.table.setItem(row, 2, QTableWidgetItem(str(user.host)))
            self.table.setItem(row, 3, QTableWidgetItem(login_str))
            self.table.setItem(row, 4, QTableWidgetItem(duration_str))

            # Alinear textos
            for col in range(5):
                self.table.item(row, col).setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
