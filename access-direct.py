#!/usr/bin/env python3
import os
import sys
from pathlib import Path

# -----------------------------
# Detectar escritorio
# -----------------------------
desktop_path = Path.home() / "Desktop"
if not desktop_path.exists():
    desktop_path = Path.home() / "Escritorio"
desktop_path.mkdir(exist_ok=True)

# -----------------------------
# Detectar ruta del ejecutable y del icono
# -----------------------------
if getattr(sys, 'frozen', False):
    exec_path = sys.executable
    icon_path = Path(exec_path).parent / "icons" / "taskmgr.svg"
else:
    exec_path = Path(__file__).parent / "main.py"
    icon_path = Path(__file__).parent / "icons" / "taskmgr.svg"

# Asegurar ruta absoluta
exec_path = str(Path(exec_path).resolve())
icon_path = str(Path(icon_path).resolve())

# -----------------------------
# Traducciones multilenguaje
# -----------------------------
translations = {
    "es": {"name": "Administrador de Tareas Lumina", "comment": "Administrador de tareas ligero estilo Windows"},
    "en": {"name": "Lumina Task Manager", "comment": "Lightweight Windows-style task manager"},
    "fr": {"name": "Gestionnaire de Tâches Lumina", "comment": "Gestionnaire de tâches léger style Windows"},
    "de": {"name": "Lumina Taskmanager", "comment": "Leichter Task-Manager im Windows-Stil"},
    "ja": {"name": "ルミナタスクマネージャー", "comment": "軽量のWindows風タスクマネージャー"}
}

lang = os.environ.get("LANG", "en")[:2]
if lang not in translations:
    lang = "en"

app_name = translations[lang]["name"]
comment = translations[lang]["comment"]

# -----------------------------
# Comando de ejecución
# -----------------------------
exec_command = f'python3 "{exec_path}"'

# -----------------------------
# Crear archivo .desktop
# -----------------------------
desktop_file_path = desktop_path / f"{app_name.replace(' ', '')}.desktop"

desktop_content = f"""[Desktop Entry]
Type=Application
Name={app_name}
Exec={exec_command}
Icon={icon_path}
Terminal=false
Categories=Utility;System;
Comment={comment}
"""

with open(desktop_file_path, "w", encoding="utf-8") as f:
    f.write(desktop_content)

# Dar permisos de ejecución
os.chmod(desktop_file_path, 0o755)

print(f"Acceso directo creado en: {desktop_file_path}")
