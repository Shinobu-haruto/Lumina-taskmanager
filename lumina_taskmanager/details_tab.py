from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem
from PyQt6.QtCore import Qt

class DetailsTab(QWidget):
    def __init__(self, lang_data, parent=None):
        # 1. Llamamos a super SOLAMENTE con parent (que es None por defecto)
        super().__init__(parent)
        
        # 2. Guardamos el diccionario por separado
        self.lang_data = lang_data
        
        self.layout = QVBoxLayout(self)
        self.setup_ui()

    def tr(self, key):
        """Sistema de traducción local."""
        return self.lang_data.get(key, key)

    def setup_ui(self):
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        # Usamos self.tr para las cabeceras
        self.table.setHorizontalHeaderLabels([
            self.tr("detail_property"), 
            self.tr("detail_value")
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.layout.addWidget(self.table)
        # ... resto de tu lógica de llenado de datos ...
