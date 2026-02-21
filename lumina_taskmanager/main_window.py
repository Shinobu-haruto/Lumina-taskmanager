from PyQt6.QtWidgets import (
    QMainWindow, QWidget,
    QHBoxLayout, QVBoxLayout,
    QListWidget, QStackedWidget,
    QMessageBox
)
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import QSize
from .styles import get_main_style
from .performance import PerformanceTab
from .processes import ProcessTab
from .details_tab import DetailsTab
from .users_tabs import UsersTab


class TaskManager(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Lumina Task Manager")
        self.resize(1000, 600)
        self.setStyleSheet(get_main_style())

        # ---------------------------
        # Barra de herramientas
        # ---------------------------
        self.toolbar = self.addToolBar("Principal")
        self.toolbar.setIconSize(QSize(24, 24))

        # Acción Ejecutar programa
        run_action = QAction(QIcon.fromTheme("system-run"), "Ejecutar", self)
        run_action.triggered.connect(self.run_program)
        self.toolbar.addAction(run_action)

        # Separador
        self.toolbar.addSeparator()

        # Acción Acerca de
        about_action = QAction(QIcon.fromTheme("help-about"), "Acerca de", self)
        about_action.triggered.connect(self.show_about)
        self.toolbar.addAction(about_action)

        # ---------------------------
        # Contenedor central
        # ---------------------------
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout()
        central.setLayout(main_layout)

        # Sidebar
        self.sidebar = QListWidget()
        self.sidebar.addItems(["Procesos", "Rendimiento", "Usuarios", "Detalles"])
        self.sidebar.setFixedWidth(200)
        self.sidebar.currentRowChanged.connect(self.change_section)
        main_layout.addWidget(self.sidebar)

        # Contenido
        self.content = QStackedWidget()
        main_layout.addWidget(self.content)

        # Inicializamos pestañas
        self.tabs = [
            ProcessTab(),
            PerformanceTab(),
            UsersTab(),
            DetailsTab()
        ]
        for tab in self.tabs:
            self.content.addWidget(tab)

        self.current_tab_index = 0
        self.sidebar.setCurrentRow(0)
        self.content.setCurrentIndex(0)

    # ---------------------------
    # Cambiar pestaña
    # ---------------------------
    def change_section(self, index):
        # Detener timer de la pestaña anterior
        prev_tab = self.tabs[self.current_tab_index]
        if hasattr(prev_tab, "stop"):
            prev_tab.stop()

        # Mostrar nueva pestaña
        self.current_tab_index = index
        self.content.setCurrentIndex(index)

    # ---------------------------
    # Ejecutar programa
    # ---------------------------
    def run_program(self):
        from PyQt6.QtWidgets import QInputDialog
        import subprocess

        prog, ok = QInputDialog.getText(self, "Ejecutar programa", "Ingrese comando:")
        if ok and prog.strip():
            try:
                subprocess.Popen(prog.strip().split())
            except Exception as e:
                QMessageBox.warning(self, "Error", f"No se pudo ejecutar:\n{e}")

    # ---------------------------
    # Acerca de
    # ---------------------------
    def show_about(self):
        QMessageBox.information(
            self,
            "Acerca de Lumina Task Manager",
            "Lumina Task Manager\nLumina Edition\nBuild: 2215\nCreado por Shinobu Haruto"
        )
