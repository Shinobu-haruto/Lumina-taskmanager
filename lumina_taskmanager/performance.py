import psutil
import pyqtgraph as pg
import platform
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTabWidget, QComboBox
from PyQt6.QtCore import QTimer

try:
    import cpuinfo
    cpuinfo_available = True
except ImportError:
    cpuinfo_available = False

class PerformanceTab(QWidget):
    def __init__(self, lang_data, parent=None):
        super().__init__(parent)
        self.lang_data = lang_data 
        self.layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        # Inicializar contadores de red para el cálculo de velocidad
        self.last_net_io = psutil.net_io_counters()

        self.setup_cpu_tab()
        self.setup_ram_tab()
        self.setup_disk_tab()
        self.setup_network_tab()

        # Timer para actualización (1 segundo)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(1000)

    def tr(self, key):
        return self.lang_data.get(key, key)

    def setup_cpu_tab(self):
        self.cpu_tab = QWidget()
        self.cpu_layout = QVBoxLayout(self.cpu_tab)
        self.cpu_name = self.get_cpu_name()
        self.cpu_label = QLabel(f"{self.cpu_name} - CPU: 0%")
        self.cpu_layout.addWidget(self.cpu_label)
        
        self.cpu_graph = pg.PlotWidget()
        self.cpu_graph.setBackground("#ffffff")
        self.cpu_graph.setYRange(0, 100)
        self.cpu_data = [0] * 60
        self.cpu_curve = self.cpu_graph.plot(pen=pg.mkPen(color="#00aa00", width=2))
        self.cpu_layout.addWidget(self.cpu_graph)
        self.tabs.addTab(self.cpu_tab, self.tr("tab_cpu"))

    def setup_ram_tab(self):
        self.ram_tab = QWidget()
        self.ram_layout = QVBoxLayout(self.ram_tab)
        self.ram_label = QLabel(f"{self.tr('tab_ram_usage')}: 0%")
        self.ram_layout.addWidget(self.ram_label)
        
        self.ram_graph = pg.PlotWidget()
        self.ram_graph.setBackground("#ffffff")
        self.ram_graph.setYRange(0, 100)
        self.ram_data = [0] * 60
        self.ram_curve = self.ram_graph.plot(pen=pg.mkPen(color="#0000aa", width=2))
        self.ram_layout.addWidget(self.ram_graph)
        self.tabs.addTab(self.ram_tab, self.tr("tab_ram"))

    def setup_disk_tab(self):
        self.disk_tab = QWidget()
        self.disk_layout = QVBoxLayout(self.disk_tab)
        self.disk_selector = QComboBox()
        self.update_disk_list()
        self.disk_layout.addWidget(self.disk_selector)
        
        self.disk_label = QLabel(f"{self.tr('tab_disks')}: 0%")
        self.disk_layout.addWidget(self.disk_label)
        
        self.disk_graph = pg.PlotWidget()
        self.disk_graph.setBackground("#ffffff")
        self.disk_graph.setYRange(0, 100)
        self.disk_data = [0] * 60
        self.disk_curve = self.disk_graph.plot(pen=pg.mkPen(color="#aa0000", width=2))
        self.disk_layout.addWidget(self.disk_graph)
        self.tabs.addTab(self.disk_tab, self.tr("tab_disks"))

    def setup_network_tab(self):
        self.net_tab = QWidget()
        self.net_layout = QVBoxLayout(self.net_tab)
        self.net_label = QLabel(f"{self.tr('tab_network')}: 0 KB/s")
        self.net_layout.addWidget(self.net_label)
        
        self.net_graph = pg.PlotWidget()
        self.net_graph.setBackground("#ffffff")
        self.net_data = [0] * 60
        self.net_curve = self.net_graph.plot(pen=pg.mkPen(color="#aa00aa", width=2))
        self.net_layout.addWidget(self.net_graph)
        self.tabs.addTab(self.net_tab, self.tr("tab_network"))

    def get_cpu_name(self):
        if cpuinfo_available:
            try: return cpuinfo.get_cpu_info().get("brand_raw", "CPU")
            except: pass
        return platform.processor() or "CPU"

    def label_disk(self, p):
        if "C:" in p.device: return self.tr("disk_master")
        if "removable" in p.opts or "usb" in p.device.lower(): return self.tr("disk_external")
        return self.tr("disk_solid")

    def update_disk_list(self):
        partitions = psutil.disk_partitions()
        for p in partitions:
            try:
                label = self.label_disk(p)
                self.disk_selector.addItem(f"{label} ({p.mountpoint})", p.mountpoint)
            except: pass

    def update_stats(self):
        # 1. Actualizar CPU
        cpu_usage = psutil.cpu_percent()
        self.cpu_data.pop(0)
        self.cpu_data.append(cpu_usage)
        self.cpu_curve.setData(self.cpu_data)
        self.cpu_label.setText(f"{self.cpu_name} - CPU: {cpu_usage}%")

        # 2. Actualizar RAM
        ram = psutil.virtual_memory()
        self.ram_data.pop(0)
        self.ram_data.append(ram.percent)
        self.ram_curve.setData(self.ram_data)
        self.ram_label.setText(f"{self.tr('tab_ram_usage')}: {ram.percent}% ({ram.used // (1024**2)} MB / {ram.total // (1024**2)} MB)")

        # 3. Actualizar Disco (basado en el seleccionado)
        try:
            path = self.disk_selector.currentData()
            disk = psutil.disk_usage(path)
            self.disk_data.pop(0)
            self.disk_data.append(disk.percent)
            self.disk_curve.setData(self.disk_data)
            self.disk_label.setText(f"{self.tr('tab_disks')} ({path}): {disk.percent}%")
        except: pass

        # 4. Actualizar Red (Velocidad KB/s)
        net_io = psutil.net_io_counters()
        # Calculamos la diferencia de bytes enviados y recibidos
        bytes_sent = net_io.bytes_sent - self.last_net_io.bytes_sent
        bytes_recv = net_io.bytes_recv - self.last_net_io.bytes_recv
        total_kb = (bytes_sent + bytes_recv) / 1024
        
        self.net_data.pop(0)
        self.net_data.append(total_kb)
        self.net_curve.setData(self.net_data)
        self.net_label.setText(f"{self.tr('tab_network')}: {total_kb:.2f} KB/s")
        self.last_net_io = net_io
