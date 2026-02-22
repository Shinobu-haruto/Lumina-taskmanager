import psutil
import pyqtgraph as pg
import socket
import time
import platform
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QCheckBox, QTabWidget, QFrame
)
from PyQt6.QtCore import QTimer

try:
    import cpuinfo
    cpuinfo_available = True
except ImportError:
    cpuinfo_available = False

class PerformanceTab(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        # Tabs
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        # ------------------- CPU -------------------
        self.cpu_tab = QWidget()
        self.cpu_layout = QVBoxLayout(self.cpu_tab)

        self.cpu_name = self.get_cpu_name()
        self.cpu_label = QLabel(f"{self.cpu_name} - Uso CPU: 0%")
        self.cpu_layout.addWidget(self.cpu_label)

        self.cpu_info_label = QLabel("GHz: 0 | Swap: 0% | Procesos: 0")
        self.cpu_layout.addWidget(self.cpu_info_label)

        self.show_cores_checkbox = QCheckBox("Mostrar núcleos")
        self.show_cores_checkbox.stateChanged.connect(self.toggle_cores)
        self.cpu_layout.addWidget(self.show_cores_checkbox)

        # CPU general graph
        self.cpu_graph = pg.PlotWidget()
        self.cpu_graph.setBackground('w')
        self.cpu_graph.setYRange(0, 100)
        self.cpu_data = [0]*60
        self.cpu_curve = self.cpu_graph.plot(pen=pg.mkPen(color='#00aa00', width=2))
        self.cpu_layout.addWidget(self.cpu_graph)

        # CPU por núcleo
        self.cores = psutil.cpu_count()
        self.core_labels = []
        self.core_graphs = []
        self.core_curves = []
        self.core_data = []

        for i in range(self.cores):
            label = QLabel(f"Core {i} - Uso: 0%")
            graph = pg.PlotWidget()
            graph.setBackground('w')
            graph.setYRange(0, 100)
            data = [0]*60
            curve = graph.plot(data, pen=pg.mkPen(color='#00aa00', width=2))
            label.hide()
            graph.hide()

            self.cpu_layout.addWidget(label)
            self.cpu_layout.addWidget(graph)

            self.core_labels.append(label)
            self.core_graphs.append(graph)
            self.core_curves.append(curve)
            self.core_data.append(data)

        self.tabs.addTab(self.cpu_tab, "CPU")

        # ------------------- RAM -------------------
        self.ram_tab = QWidget()
        self.ram_layout = QVBoxLayout(self.ram_tab)

        self.ram_label = QLabel("RAM - Uso: 0%")
        self.ram_layout.addWidget(self.ram_label)

        self.ram_graph = pg.PlotWidget()
        self.ram_graph.setBackground('w')
        self.ram_graph.setYRange(0, 100)
        self.ram_data = [0]*60
        self.ram_curve = self.ram_graph.plot(pen=pg.mkPen(color='#0000aa', width=2))
        self.ram_layout.addWidget(self.ram_graph)

        total_ram = psutil.virtual_memory().total // (1024*1024)
        self.ram_info_label = QLabel(f"RAM total: {total_ram} MB")
        self.ram_layout.addWidget(self.ram_info_label)

        self.tabs.addTab(self.ram_tab, "RAM")

        # ------------------- Discos -------------------
        self.disk_tab = QWidget()
        self.disk_layout = QVBoxLayout(self.disk_tab)

        self.disk_label = QLabel("Disco (MB/s)")
        self.disk_layout.addWidget(self.disk_label)

        self.disk_graph = pg.PlotWidget()
        self.disk_graph.setBackground('w')
        self.disk_graph.setYRange(0, 100)
        self.disk_data = [0]*60
        self.disk_curve = self.disk_graph.plot(pen=pg.mkPen(color='#aa0000', width=2))
        self.disk_layout.addWidget(self.disk_graph)

        self.disk_read_label = QLabel("Lectura: 0 MB/s")
        self.disk_write_label = QLabel("Escritura: 0 MB/s")
        self.disk_layout.addWidget(self.disk_read_label)
        self.disk_layout.addWidget(self.disk_write_label)

        disk = psutil.disk_io_counters()
        self.last_read = disk.read_bytes
        self.last_write = disk.write_bytes

        self.tabs.addTab(self.disk_tab, "Discos")

        # ------------------- Red -------------------
        self.net_tab = QWidget()
        self.net_layout = QVBoxLayout(self.net_tab)

        self.net_label = QLabel("Red (MB/s)")
        self.net_layout.addWidget(self.net_label)

        self.net_graph = pg.PlotWidget()
        self.net_graph.setBackground('w')
        self.net_graph.setYRange(0, 50)
        self.net_data = [0]*60
        self.net_curve = self.net_graph.plot(pen=pg.mkPen(color='#aa00aa', width=2))
        self.net_layout.addWidget(self.net_graph)

        self.net_sent_label = QLabel("Enviados: 0 MB/s")
        self.net_recv_label = QLabel("Recibidos: 0 MB/s")
        self.net_layout.addWidget(self.net_sent_label)
        self.net_layout.addWidget(self.net_recv_label)

        net = psutil.net_io_counters()
        self.last_sent = net.bytes_sent
        self.last_recv = net.bytes_recv

        self.tabs.addTab(self.net_tab, "Red")

        # Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(1000)

    def get_cpu_name(self):
        if cpuinfo_available:
            info = cpuinfo.get_cpu_info()
            return info['brand_raw']
        else:
            return platform.processor() or "CPU Desconocido"

    def toggle_cores(self):
        show = self.show_cores_checkbox.isChecked()
        for i in range(self.cores):
            self.core_labels[i].setVisible(show)
            self.core_graphs[i].setVisible(show)

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
        # CPU
        cpu_percent = psutil.cpu_percent()
        self.cpu_data.pop(0)
        self.cpu_data.append(cpu_percent)
        self.cpu_curve.setData(self.cpu_data)

        cpu_freq = psutil.cpu_freq()
        freq = cpu_freq.current/1000 if cpu_freq else 0  # GHz
        swap_percent = psutil.swap_memory().percent
        num_procs = len(psutil.pids())

        self.cpu_label.setText(f"{self.cpu_name} - Uso CPU: {cpu_percent:.1f}%")
        self.cpu_info_label.setText(f"GHz: {freq:.2f} | Swap: {swap_percent:.1f}% | Procesos: {num_procs}")

        # CPU por núcleo
        cpu_per_core = psutil.cpu_percent(percpu=True)
        for i, usage in enumerate(cpu_per_core):
            self.core_data[i].pop(0)
            self.core_data[i].append(usage)
            self.core_curves[i].setData(self.core_data[i])
            self.core_labels[i].setText(f"Core {i} - Uso: {usage:.1f}%")

        # RAM
        ram_percent = psutil.virtual_memory().percent
        self.ram_data.pop(0)
        self.ram_data.append(ram_percent)
        self.ram_curve.setData(self.ram_data)
        self.ram_label.setText(f"RAM - Uso: {ram_percent:.1f}%")

        # Discos
        disk = psutil.disk_io_counters()
        read_speed = (disk.read_bytes - self.last_read)/(1024*1024)
        write_speed = (disk.write_bytes - self.last_write)/(1024*1024)
        self.last_read = disk.read_bytes
        self.last_write = disk.write_bytes
        total_speed = read_speed + write_speed
        self.disk_data.pop(0)
        self.disk_data.append(total_speed)
        self.disk_curve.setData(self.disk_data)
        self.disk_read_label.setText(f"Lectura: {read_speed:.1f} MB/s")
        self.disk_write_label.setText(f"Escritura: {write_speed:.1f} MB/s")

        # Red
        net = psutil.net_io_counters()
        sent_speed = (net.bytes_sent - self.last_sent)/(1024*1024)
        recv_speed = (net.bytes_recv - self.last_recv)/(1024*1024)
        self.last_sent = net.bytes_sent
        self.last_recv = net.bytes_recv
        total_net = sent_speed + recv_speed
        self.net_data.pop(0)
        self.net_data.append(total_net)
        self.net_curve.setData(self.net_data)
        self.net_sent_label.setText(f"Enviados: {sent_speed:.1f} MB/s")
        self.net_recv_label.setText(f"Recibidos: {recv_speed:.1f} MB/s")
