import psutil
import pyqtgraph as pg
import socket
import time

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QMenu
from PyQt6.QtGui import QAction
from PyQt6.QtCore import QTimer, Qt

try:
    import GPUtil
    gpu_available = True
except ImportError:
    gpu_available = False

class PerformanceTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)

        self.show_cores = False  # Flag para mostrar núcleos

        # ----- CPU TOTAL -----
        self.cpu_label = QLabel("CPU Total (clic derecho para opciones)")
        self.cpu_label.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.cpu_label.customContextMenuRequested.connect(self.open_cpu_menu)
        self.layout.addWidget(self.cpu_label)

        self.cpu_graph = pg.PlotWidget()
        self.cpu_graph.setYRange(0, 100)
        self.cpu_graph.setBackground('#ffffff')
        self.layout.addWidget(self.cpu_graph)
        self.cpu_data = [0] * 60
        self.cpu_curve = self.cpu_graph.plot(self.cpu_data, pen=pg.mkPen(color='#00aa00', width=2))

        # ----- CPU POR NÚCLEO -----
        self.core_graphs = []
        self.core_curves = []
        self.core_data = []
        self.core_labels = []
        self.core_container = QVBoxLayout()
        self.layout.addLayout(self.core_container)

        self.cores = psutil.cpu_count()
        for i in range(self.cores):
            label = QLabel(f"CPU Core {i}")
            graph = pg.PlotWidget()
            graph.setYRange(0, 100)
            graph.setBackground('#ffffff')
            data = [0] * 60
            curve = graph.plot(data, pen=pg.mkPen(color='#00aa00', width=2))

            self.core_labels.append(label)
            self.core_graphs.append(graph)
            self.core_curves.append(curve)
            self.core_data.append(data)

            # Inicialmente ocultos
            label.hide()
            graph.hide()
            self.core_container.addWidget(label)
            self.core_container.addWidget(graph)

        # ----- RAM -----
        self.layout.addWidget(QLabel("Memoria"))
        self.ram_graph = pg.PlotWidget()
        self.ram_graph.setYRange(0, 100)
        self.ram_graph.setBackground('#ffffff')
        self.layout.addWidget(self.ram_graph)
        self.ram_data = [0] * 60
        self.ram_curve = self.ram_graph.plot(self.ram_data, pen=pg.mkPen(color='#00aa00', width=2))

        # ----- DISCO -----
        self.layout.addWidget(QLabel("Disco (MB/s)"))
        self.disk_graph = pg.PlotWidget()
        self.disk_graph.setYRange(0, 100)
        self.disk_graph.setBackground('#ffffff')
        self.layout.addWidget(self.disk_graph)
        self.disk_data = [0] * 60
        self.disk_curve = self.disk_graph.plot(self.disk_data, pen=pg.mkPen(color='#00aa00', width=2))
        disk = psutil.disk_io_counters()
        self.last_read = disk.read_bytes
        self.last_write = disk.write_bytes

        # ----- RED -----
        self.layout.addWidget(QLabel("Red (MB/s)"))
        self.net_graph = pg.PlotWidget()
        self.net_graph.setYRange(0, 50)
        self.net_graph.setBackground('#ffffff')
        self.layout.addWidget(self.net_graph)
        self.net_data = [0] * 60
        self.net_curve = self.net_graph.plot(self.net_data, pen=pg.mkPen(color='#00aa00', width=2))
        net = psutil.net_io_counters()
        self.last_sent = net.bytes_sent
        self.last_recv = net.bytes_recv

        # ----- GPU -----
        if gpu_available:
            self.layout.addWidget(QLabel("GPU (%)"))
            self.gpu_graph = pg.PlotWidget()
            self.gpu_graph.setYRange(0, 100)
            self.gpu_graph.setBackground('#ffffff')
            self.layout.addWidget(self.gpu_graph)
            self.gpu_data = [0] * 60
            self.gpu_curve = self.gpu_graph.plot(self.gpu_data, pen=pg.mkPen(color='#00aa00', width=2))

        # ----- INFO SISTEMA -----
        self.uptime_label = QLabel("Uptime: ")
        self.ip_label = QLabel("IP: ")
        self.layout.addWidget(self.uptime_label)
        self.layout.addWidget(self.ip_label)

        # Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(1000)

    # Menu contextual para mostrar núcleos
    def open_cpu_menu(self, position):
        menu = QMenu()
        toggle_action = QAction("Mostrar todos los núcleos", self)
        toggle_action.setCheckable(True)
        toggle_action.setChecked(self.show_cores)
        toggle_action.triggered.connect(self.toggle_cores)
        menu.addAction(toggle_action)
        menu.exec(self.cpu_label.mapToGlobal(position))

    def toggle_cores(self):
        self.show_cores = not self.show_cores
        for i in range(self.cores):
            if self.show_cores:
                self.core_labels[i].show()
                self.core_graphs[i].show()
            else:
                self.core_labels[i].hide()
                self.core_graphs[i].hide()

    def get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "No disponible"

    def update_stats(self):
        # CPU total
        cpu_total = psutil.cpu_percent()
        self.cpu_data.pop(0)
        self.cpu_data.append(cpu_total)
        self.cpu_curve.setData(self.cpu_data)

        # CPU por núcleo
        cpu_per_core = psutil.cpu_percent(percpu=True)
        for i, usage in enumerate(cpu_per_core):
            self.core_data[i].pop(0)
            self.core_data[i].append(usage)
            self.core_curves[i].setData(self.core_data[i])

        # RAM
        ram = psutil.virtual_memory().percent
        self.ram_data.pop(0)
        self.ram_data.append(ram)
        self.ram_curve.setData(self.ram_data)

        # DISCO
        disk = psutil.disk_io_counters()
        read_speed = (disk.read_bytes - self.last_read) / (1024 * 1024)
        write_speed = (disk.write_bytes - self.last_write) / (1024 * 1024)
        total_speed = read_speed + write_speed
        self.last_read = disk.read_bytes
        self.last_write = disk.write_bytes
        self.disk_data.pop(0)
        self.disk_data.append(total_speed)
        self.disk_curve.setData(self.disk_data)

        # RED
        net = psutil.net_io_counters()
        sent_speed = (net.bytes_sent - self.last_sent) / (1024 * 1024)
        recv_speed = (net.bytes_recv - self.last_recv) / (1024 * 1024)
        total_net = sent_speed + recv_speed
        self.last_sent = net.bytes_sent
        self.last_recv = net.bytes_recv
        self.net_data.pop(0)
        self.net_data.append(total_net)
        self.net_curve.setData(self.net_data)

        # GPU
        if gpu_available:
            gpus = GPUtil.getGPUs()
            usage = gpus[0].load * 100 if gpus else 0
            self.gpu_data.pop(0)
            self.gpu_data.append(usage)
            self.gpu_curve.setData(self.gpu_data)

        # Uptime
        boot_time = psutil.boot_time()
        uptime_seconds = int(time.time() - boot_time)
        days = uptime_seconds // 86400
        hours = (uptime_seconds % 86400) // 3600
        minutes = (uptime_seconds % 3600) // 60
        self.uptime_label.setText(f"Uptime: {days}d {hours}h {minutes}m")

        # IP
        ip = self.get_local_ip()
        self.ip_label.setText(f"IP: {ip}")

    def stop(self):
        self.timer.stop()
