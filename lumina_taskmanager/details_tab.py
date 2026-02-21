from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
import psutil


class DetailsTab(QWidget):

    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout(self)

        self.info_label = QLabel("Selecciona un proceso...")
        self.layout.addWidget(self.info_label)

    def show_process_details(self, pid):
        try:
            process = psutil.Process(pid)

            info = (
                f"PID: {pid}\n"
                f"Nombre: {process.name()}\n"
                f"Estado: {process.status()}\n"
                f"Usuario: {process.username()}\n"
                f"Memoria: {process.memory_percent():.2f}%\n"
                f"Threads: {process.num_threads()}\n"
                f"CPU Time: {sum(process.cpu_times())}"
            )

            self.info_label.setText(info)

        except psutil.NoSuchProcess:
            self.info_label.setText("Proceso no disponible.")
