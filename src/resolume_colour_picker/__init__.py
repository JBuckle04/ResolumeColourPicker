import copy
import json
import sys
import requests
import time
from importlib.resources import files
from concurrent.futures import ThreadPoolExecutor

from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton,
    QGridLayout, QLabel, QVBoxLayout, QHBoxLayout,
    QDialog, QTableWidget, QTableWidgetItem, QLineEdit,
    QHeaderView, QColorDialog
)
from PySide6.QtCore import Qt, QTimer, Signal, QObject
from PySide6.QtGui import QColor, QPalette

from resolume_colour_picker.application import ColourPickerEngine
from resolume_colour_picker.config import Config

# =========================
# CONFIGURATION
# =========================

COLUMNS = ["ALL" , "Outer", "Middle", "Inner", "DJ"]
ALL_COLUMN = "ALL"

# Define colours as a dictionary
_COLOUR_SET = {
    "1 - Red": "#FF0000",
    "2 - Blue": "#0000FF",
    "3 - Yellow": "#FFFF00",
    "4 - Orange": "#FFA500",
    "5 - Green": "#00B050",
    "6 - Purple": "#800080",
    "7 - Pink": "#FF69B4",
    "8 - White": "#FFFFFF",
}

# Convert to list maintaining order
COLOUR_ROWS = list(_COLOUR_SET.items())

CONSTS = {
    "WINDOW_SIZE": (900, 700),
    "BUTTON_HEIGHT": 55,
    "DARKEN_FACTOR": 0.65,
    "HEARTBEAT_INTERVAL": 3000  # 3 seconds in milliseconds
}


WEBSERVER_IP = "localhost"
WEBSERVER_PORT = 8080
API_BASE_URL = f"http://{WEBSERVER_IP}:{WEBSERVER_PORT}/api/v1/composition"

LAYER_MAP = {
    "Inner": 1,
    "Middle": 2,
    "Outer": 3,
    "DJ": 4,
}

RESOLUME_PRODUCT_URL = f"http://{WEBSERVER_IP}:{WEBSERVER_PORT}/api/v1/product"






# =========================
# STATUS HEARTBEAT
# =========================

# =========================
# DARK THEME SETUP
# =========================

def apply_dark_theme(app):
    """Apply a dark theme to the application"""
    # Force Fusion style for consistent look across platforms
    app.setStyle("Fusion")
    
    # Create dark palette
    dark_palette = QPalette()
    
    # Base colors
    dark_palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.ColorRole.Base, QColor(35, 35, 35))
    dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(25, 25, 25))
    dark_palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
    dark_palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.ColorRole.HighlightedText, QColor(0, 0, 0))
    
    # Disabled colors
    dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, QColor(127, 127, 127))
    dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(127, 127, 127))
    dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(127, 127, 127))
    dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Highlight, QColor(80, 80, 80))
    dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.HighlightedText, QColor(127, 127, 127))
    
    app.setPalette(dark_palette)
    
    # Additional stylesheet for finer control
    app.setStyleSheet("""
        QToolTip {
            color: #ffffff;
            background-color: #2a2a2a;
            border: 1px solid #555555;
        }
        QLineEdit {
            background-color: #2b2b2b;
            border: 1px solid #555555;
            border-radius: 3px;
            padding: 3px;
        }
        QLineEdit:focus {
            border: 1px solid #2a82da;
        }
    """)

# =========================
# MAIN APP
# =========================


def start():
    defaults = json.loads(
        files("resolume_colour_picker.data")
        .joinpath("defaults.json")
        .read_text(encoding="utf-8")
    )

    app = QApplication(sys.argv)
    
    # Apply dark theme
    apply_dark_theme(app)
    
    config = Config("Colour Picker Engine", defaults=defaults)
    window = ColourPickerEngine(config, CONSTS)
    window.show()
    app.aboutToQuit.connect(config.save)
    sys.exit(app.exec())