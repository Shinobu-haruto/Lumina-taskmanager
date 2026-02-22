from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QStackedWidget, QMessageBox
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize, Qt
from .styles import get_main_style
from .performance import PerformanceTab
from .processes import ProcessTab
from .details_tab import DetailsTab
from .users_tabs import UsersTab
import subprocess

class TaskManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lumina Task Manager")
        self.resize(1000, 600)
        self.setStyleSheet(get_main_style())

        # ---------------------------
        # Toolbar minimalista
        # ---------------------------
        self.toolbar = self.addToolBar("Principal")
        self.toolbar.setIconSize(QSize(28, 28))
        self.toolbar.setMovable(False)
        self.toolbar.setStyleSheet("""
            QToolBar {
                background-color: #eceff4;
                border-bottom: 1px solid #d8dee9;
            }
            QToolButton {
                border: none;
                padding: 5px;
            }
            QToolButton:hover {
                background-color: #81a1c1;
                border-radius: 5px;
            }
        """)

        run_action = self.toolbar.addAction(QIcon.fromTheme("system-run"), "")
        run_action.setToolTip("Ejecutar programa")
        run_action.triggered.connect(self.run_program)

        self.toolbar.addSeparator()

        about_action = self.toolbar.addAction(QIcon.fromTheme("help-about"), "")
        about_action.setToolTip("Acerca de Lumina")
        about_action.triggered.connect(self.show_about)

        # ---------------------------
        # Contenedor central
        # ---------------------------
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout()
        central.setLayout(main_layout)

        # ---------------------------
        # Panel de “Card Tabs”
        # ---------------------------
        self.card_panel = QWidget()
        card_layout = QVBoxLayout()
        card_layout.setSpacing(12)
        card_layout.setContentsMargins(10, 10, 10, 10)
        self.card_panel.setLayout(card_layout)
        self.card_panel.setFixedWidth(200)
        main_layout.addWidget(self.card_panel)

        self.tabs_info = [
            ("Procesos", "utilities-system-monitor"),
            ("Rendimiento", "view-statistics"),
            ("Usuarios", "system-users"),
            ("Detalles", "dialog-information")
        ]

        self.tab_buttons = []
        for index, (name, icon_name) in enumerate(self.tabs_info):
            btn = QPushButton(name)
            btn.setIcon(QIcon.fromTheme(icon_name))
            btn.setIconSize(QSize(24,24))
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, i=index: self.switch_tab(i))
            btn.setStyleSheet(self.card_style(unselected=True))
            card_layout.addWidget(btn)
            self.tab_buttons.append(btn)

        # Seleccionar la primera pestaña por defecto
        self.tab_buttons[0].setChecked(True)
        self.tab_buttons[0].setStyleSheet(self.card_style(unselected=False))

        # ---------------------------
        # Contenido con bordes redondeados
        # ---------------------------
        self.content = QStackedWidget()
        self.content.setStyleSheet("""
            QStackedWidget {
                background-color: #eceff4;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        main_layout.addWidget(self.content)

        # Inicializamos pestañas
        self.tabs = [
            ProcessTab(),
            PerformanceTab(),
            UsersTab(),
            DetailsTab()
        ]
        for tab in self.tabs:
            tab.setStyleSheet("""
                QWidget {
                    background-color: #eceff4;
                }
            """)
            self.content.addWidget(tab)

        self.current_tab_index = 0

        # ---------------------------
        # Barra de estado
        # ---------------------------
        self.statusBar().showMessage(f"Sección: {self.tabs_info[0][0]}")

    # ---------------------------
    # Cambiar pestaña
    # ---------------------------
    def switch_tab(self, index):
        # Detener timer de la pestaña anterior
        prev_tab = self.tabs[self.current_tab_index]
        if hasattr(prev_tab, "stop"):
            prev_tab.stop()

        # Actualizar contenido
        self.current_tab_index = index
        self.content.setCurrentIndex(index)
        self.statusBar().showMessage(f"Sección: {self.tabs_info[index][0]}")

        # Actualizar estilos de los botones tipo card
        for i, btn in enumerate(self.tab_buttons):
            if i == index:
                btn.setChecked(True)
                btn.setStyleSheet(self.card_style(unselected=False))
            else:
                btn.setChecked(False)
                btn.setStyleSheet(self.card_style(unselected=True))

    # ---------------------------
    # Estilo para botones tipo card
    # ---------------------------
    def card_style(self, unselected=True):
        if unselected:
            return """
                QPushButton {
                    background-color: #2e3440;
                    color: #d8dee9;
                    border: none;
                    border-radius: 8px;
                    padding: 12px;
                    text-align: left;
                }
                QPushButton:hover {
                    background-color: #5e81ac;
                }
            """
        else:
            return """
                QPushButton {
                    background-color: #81a1c1;
                    color: #2e3440;
                    font-weight: bold;
                    border-radius: 8px;
                    padding: 12px;
                    text-align: left;
                }
            """

    # ---------------------------
    # Ejecutar programa
    # ---------------------------
    def run_program(self):
        from PyQt6.QtWidgets import QInputDialog
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
            "Lumina Task Manager\nVersión 1.0\nCreado por Shinobu"
        )
