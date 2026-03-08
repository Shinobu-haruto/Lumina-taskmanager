import os
import json
import shlex
import locale
import platform
import subprocess

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QPushButton, QStackedWidget, 
    QMessageBox, QDialog, QLabel, QSplitter, QLineEdit, QFrame, QInputDialog
)
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import QSize, Qt

from lumina_taskmanager.styles import get_main_style, LUMINA_BUILD_DATA
from lumina_taskmanager.performance import PerformanceTab
from lumina_taskmanager.processes import ProcessTab
from lumina_taskmanager.details_tab import DetailsTab
from lumina_taskmanager.users_tabs import UsersTab
from lumina_taskmanager.startup_tab import StartupTab

class TaskManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.load_translations()
        self.setWindowTitle(f"{LUMINA_BUILD_DATA['Brand']} Task Manager")
        self.resize(800, 600)
        self.setMinimumSize(600, 400)
        self.setStyleSheet(get_main_style())
        self.setup_ui()

    def load_translations(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(base_dir, "languages.json")
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                all_langs = json.load(f)
        except:
            all_langs = {"en": {}}
        
        sys_lang = locale.getdefaultlocale()[0]
        lang_code = sys_lang.split('_')[0] if sys_lang else "en"
        # Obtiene el diccionario del idioma
        data = all_langs.get(lang_code, all_langs.get("en", {}))
        
        # Manejo de referencia si existe
        if "ref" in data:
            self.lang_data = all_langs.get(data["ref"], all_langs.get("en", {}))
        else:
            self.lang_data = data

    def tr(self, key):
        return self.lang_data.get(key, key)

    def setup_ui(self):
        self.toolbar = self.addToolBar("Principal")
        self.toolbar.setIconSize(QSize(18, 18))
        
        run_act = self.toolbar.addAction(QIcon.fromTheme("system-run"), "")
        run_act.setToolTip(self.tr("run_tooltip"))
        run_act.triggered.connect(self.run_program)
        self.toolbar.addSeparator()
        about_act = self.toolbar.addAction(QIcon.fromTheme("help-about"), "")
        about_act.setToolTip(self.tr("about_tooltip"))
        about_act.triggered.connect(self.show_about)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText(self.tr("search_placeholder"))
        self.search_bar.textChanged.connect(self.filter_content)
        main_layout.addWidget(self.search_bar)

        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(self.splitter)
        self.setup_sidebar()
        self.setup_content_area()
        self.splitter.addWidget(self.card_panel)
        self.splitter.addWidget(self.content)
        self.splitter.setSizes([200, 900])
        self.statusBar().showMessage(f"{self.tr('status_section')}: {self.tabs_info[0][0]}")

    def setup_sidebar(self):
        self.card_panel = QWidget()
        self.card_panel.setMinimumWidth(160)
        card_layout = QVBoxLayout(self.card_panel)
        self.tabs_info = [
            (self.tr("tab_processes"), "utilities-system-monitor"),
            (self.tr("tab_performance"), "view-statistics"),
            (self.tr("tab_users"), "system-users"),
            (self.tr("tab_details"), "dialog-information"),
            (self.tr("tab_startup"), "system-run")
        ]
        self.tab_buttons = []
        for index, (name, icon) in enumerate(self.tabs_info):
            btn = QPushButton(name)
            btn.setIcon(QIcon.fromTheme(icon))
            btn.setCheckable(True)
            btn.clicked.connect(lambda _, i=index: self.switch_tab(i))
            card_layout.addWidget(btn)
            self.tab_buttons.append(btn)
        card_layout.addStretch()
        self.tab_buttons[0].setChecked(True)

    def setup_content_area(self):
        self.content = QStackedWidget()
        # 
        # Inyectamos el diccionario de traducción (self.lang_data) en cada constructor
        tabs = [
            ProcessTab(self.lang_data), 
            PerformanceTab(self.lang_data), 
            UsersTab(self.lang_data), 
            DetailsTab(self.lang_data), 
            StartupTab(self.lang_data)
        ]
        for tab in tabs:
            self.content.addWidget(tab)

    def switch_tab(self, index):
        self.content.setCurrentIndex(index)
        for i, btn in enumerate(self.tab_buttons):
            btn.setChecked(i == index)
        self.statusBar().showMessage(f"{self.tr('status_section')}: {self.tabs_info[index][0]}")

    def filter_content(self, text):
        tab = self.content.currentWidget()
        if hasattr(tab, "filter_data"): tab.filter_data(text)

    def run_program(self):
        cmd, ok = QInputDialog.getText(self, self.tr("run_title"), self.tr("run_label"))
        if ok and cmd:
            try: subprocess.Popen(shlex.split(cmd))
            except Exception as e: QMessageBox.warning(self, self.tr("error_title"), str(e))

    def show_about(self):
        dialog = QDialog(self)
        dialog.setWindowTitle(self.tr("about_tooltip"))
        dialog.setFixedSize(520, 520)
        dialog.setStyleSheet("background-color: #ffffff; color: #2e3440;")
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(40, 30, 40, 30)

        logo_label = QLabel()
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logo_path = os.path.join(base_dir, "branding", "lumina_logo.png")
        if os.path.exists(logo_path):
            logo_label.setPixmap(QPixmap(logo_path).scaled(280, 70, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            logo_label.setText(f"<h1 style='color: #5e81ac;'>{LUMINA_BUILD_DATA['Brand']}</h1>")
        layout.addWidget(logo_label)

        title = QLabel(f"{LUMINA_BUILD_DATA['Brand']} Professional")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #2e3440; margin-top: 10px;")
        layout.addWidget(title)
        
        version_text = f"{self.tr('label_version')} {LUMINA_BUILD_DATA['Release']} (Build {LUMINA_BUILD_DATA['Build']})"
        version_label = QLabel(version_text)
        version_label.setStyleSheet("font-size: 13px; color: #4c566a;")
        layout.addWidget(version_label)

        tech_label = QLabel(f"{LUMINA_BUILD_DATA['Channel'].upper()} | {LUMINA_BUILD_DATA['Codename']}")
        tech_label.setStyleSheet("font-size: 11px; color: #888; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(tech_label)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("color: #d8dee9; margin: 10px 0px;")
        layout.addWidget(line)

        layout.addWidget(QLabel(f"<b>{self.tr('spec_device')}</b>"))
        sys_info = QLabel(
            f"{self.tr('label_processor')}: {platform.processor() or 'N/A'}\n"
            f"{self.tr('label_dev_name')}: {platform.node() or 'N/A'}\n"
            f"{self.tr('label_sys_type')}: {platform.system()} {platform.machine()}"
        )
        sys_info.setStyleSheet("color: #4c566a; font-size: 12px; margin-left: 10px; line-height: 150%;")
        layout.addWidget(sys_info)

        layout.addStretch()
        footer_label = QLabel(self.tr("copyright"))
        footer_label.setStyleSheet("font-size: 10px; color: #b4b4b4; text-align: center;")
        footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(footer_label)
        
        btn_close = QPushButton(self.tr("btn_close"))
        btn_close.setFixedWidth(100)
        btn_close.clicked.connect(dialog.accept)
        btn_close.setStyleSheet("QPushButton { background-color: #f3f3f3; border: 1px solid #ccc; padding: 6px; }")
        layout.addWidget(btn_close, alignment=Qt.AlignmentFlag.AlignCenter)
        dialog.exec()
