"""RPX Pro Entry Point: Initialisierung und Start."""

import sys

from rpx_pro.constants import (
    APP_TITLE, VERSION, ensure_directories, setup_logging, _init_audio_backend,
)


def main():
    """Haupteinstiegspunkt fuer RPX Pro."""
    # Verzeichnisse und Logging initialisieren
    ensure_directories()
    setup_logging()

    # PySide6 importieren (erst nach Logging-Setup)
    from PySide6.QtWidgets import QApplication
    from PySide6.QtGui import QPalette, QColor
    from PySide6.QtCore import Qt

    app = QApplication(sys.argv)
    app.setApplicationName(APP_TITLE)

    # Dark Theme
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(30, 30, 46))
    palette.setColor(QPalette.WindowText, QColor(205, 214, 244))
    palette.setColor(QPalette.Base, QColor(24, 24, 37))
    palette.setColor(QPalette.AlternateBase, QColor(30, 30, 46))
    palette.setColor(QPalette.ToolTipBase, QColor(49, 50, 68))
    palette.setColor(QPalette.ToolTipText, QColor(205, 214, 244))
    palette.setColor(QPalette.Text, QColor(205, 214, 244))
    palette.setColor(QPalette.Button, QColor(49, 50, 68))
    palette.setColor(QPalette.ButtonText, QColor(205, 214, 244))
    palette.setColor(QPalette.BrightText, QColor(243, 139, 168))
    palette.setColor(QPalette.Link, QColor(137, 180, 250))
    palette.setColor(QPalette.Highlight, QColor(137, 180, 250))
    palette.setColor(QPalette.HighlightedText, QColor(30, 30, 46))
    app.setPalette(palette)

    # Audio-Backend nach QApplication initialisieren
    _init_audio_backend()

    # CLI-Modus pruefen
    cli_mode = "--cli" in sys.argv

    # MainWindow importieren und starten
    from rpx_pro.main_window import RPXProMainWindow
    window = RPXProMainWindow()
    window.show()

    # Optional CLI starten
    if cli_mode:
        from rpx_pro.api import RPXProAPI
        from rpx_pro.cli import CLIInterface
        api = RPXProAPI(window.data_manager)
        cli = CLIInterface(api)
        cli.start()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
