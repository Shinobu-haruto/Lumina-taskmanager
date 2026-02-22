from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QHBoxLayout
import psutil
import time

class DetailsTab(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        self.info_frame = QFrame()
        self.info_layout = QVBoxLayout(self.info_frame)

        self.general_label = QLabel("Selecciona un proceso...")
        self.cpu_label = QLabel("")
        self.memory_label = QLabel("")
        self.threads_label = QLabel("")

        self.info_layout.addWidget(self.general_label)
        self.info_layout.addWidget(self.cpu_label)
        self.info_layout.addWidget(self.memory_label)
        self.info_layout.addWidget(self.threads_label)

        self.layout.addWidget(self.info_frame)

    def show_process_details(self, pid):
        try:
            process = psutil.Process(pid)

            # General
            general_info = f"PID: {pid} | Nombre: {process.name()} | Estado: {process.status()} | Usuario: {process.username()}"
            self.general_label.setText(general_info)

            # CPU
            cpu_times = process.cpu_times()
            total_cpu_seconds = sum(cpu_times)
            hours = int(total_cpu_seconds // 3600)
            minutes = int((total_cpu_seconds % 3600) // 60)
            seconds = int(total_cpu_seconds % 60)
            self.cpu_label.setText(f"Tiempo CPU: {hours}h {minutes}m {seconds}s | CPU%: {process.cpu_percent(interval=0.1):.1f}%")

            # Memoria
            mem_info = process.memory_info()
            mem_mb = mem_info.rss / (1024*1024)
            self.memory_label.setText(f"Memoria: {mem_mb:.1f} MB ({process.memory_percent():.2f}%)")

            # Threads
            self.threads_label.setText(f"Hilos: {process.num_threads()}")

        except psutil.NoSuchProcess:
            self.general_label.setText("Proceso no disponible.")
            self.cpu_label.setText("")
            self.memory_label.setText("")
            self.threads_label.setText("")
