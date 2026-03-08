import os
import glob
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt6.QtCore import Qt

class StartupTab(QWidget):
    def __init__(self, lang_data, parent=None):
        # 1. Pasamos el parent correcto a QWidget
        super().__init__(parent)
        
        # 2. Guardamos el diccionario de idiomas
        self.lang_data = lang_data
        
        self.layout = QVBoxLayout(self)
        
        self.table = QTableWidget()
        self.table.setColumnCount(1)
        
        # 3. Usamos nuestro propio método tr()
        self.table.setHorizontalHeaderLabels([self.tr("startup_header")])
        
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.setStyleSheet("border: none; background-color: #ffffff;")
        
        self.layout.addWidget(self.table)
        self.load_startup_items()

    def tr(self, key):
        """Traducción local usando el diccionario inyectado."""
        return self.lang_data.get(key, key)

    def load_startup_items(self):
        # Detectamos la carpeta de inicio según el SO
        items = []
        if os.name == 'nt':  # Windows
            appdata = os.environ.get('APPDATA', '')
            startup_path = os.path.join(appdata, r'Microsoft\Windows\Start Menu\Programs\Startup', '*.lnk')
            items = glob.glob(startup_path)
        else:  # Linux (Autostart .desktop files)
            config_home = os.environ.get('XDG_CONFIG_HOME', os.path.expanduser('~/.config'))
            startup_path = os.path.join(config_home, 'autostart', '*.desktop')
            items = glob.glob(startup_path)
        
        self.table.setRowCount(len(items))
        
        for row, item_path in enumerate(items):
            file_name = os.path.basename(item_path).replace('.lnk', '').replace('.desktop', '')
            item = QTableWidgetItem(file_name)
            self.table.setItem(row, 0, item)
