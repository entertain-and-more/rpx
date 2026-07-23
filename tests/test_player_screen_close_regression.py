# -*- coding: utf-8 -*-
"""Regression fuer FABLE-SOL Software-Loop Punkt 26 (2026-07-23).

Bug (AUFGABEN.txt, main_window Z.743): Direktes Schliessen des Spieler-Bildschirms
(Alt+F4, Fenster-X) wurde nicht erkannt, weil nur der Menue-Toggle-Pfad
`self.player_screen = None` setzte und Button/Menue-Text zuruecksetzte. Das
liess `self.player_screen` auf ein bereits geschlossenes Fenster zeigen
(State-Desync) und erzeugte pro Toggle-Zyklus ein Widget-Leak, da das alte
QMainWindow-Objekt nie zerstoert wurde.

Fix: `PlayerScreen` setzt `Qt.WA_DeleteOnClose` und emittiert ein `closed`-Signal
aus `closeEvent()`. `MainWindow` haengt die gesamte Aufraeumlogik (Referenz
zuruecksetzen, Menue-/Button-Text, Statusbar) einmalig in `_on_player_screen_closed`
auf, das sowohl beim Menue-Toggle als auch beim Direktschliessen laeuft.
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

ROOT = Path(__file__).parent.parent
RPX = ROOT / "rpx_pro"
sys.path.insert(0, str(ROOT))

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication


def _src(rel: str) -> str:
    return (RPX / rel).read_text(encoding="utf-8")


def _app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_player_screen_sets_delete_on_close():
    _app()
    from rpx_pro.widgets.player_screen import PlayerScreen

    screen = PlayerScreen()
    assert screen.testAttribute(Qt.WA_DeleteOnClose)


def test_player_screen_emits_closed_signal_on_close_event():
    _app()
    from rpx_pro.widgets.player_screen import PlayerScreen

    screen = PlayerScreen()
    fired = []
    screen.closed.connect(lambda: fired.append(True))

    screen.close()

    assert fired == [True]


def test_main_window_registers_single_cleanup_handler():
    src = _src("main_window.py")
    assert "def _on_player_screen_closed(self):" in src
    assert "self.player_screen.closed.connect(self._on_player_screen_closed)" in src
    # Der Menue-Toggle-Close-Pfad darf den Reset nicht mehr doppelt inline machen --
    # sonst laeuft er beim Direktschliessen (Alt+F4) wieder auseinander.
    toggle_start = src.index("def _toggle_player_screen(self):")
    cleanup_start = src.index("def _on_player_screen_closed(self):")
    toggle_body = src[toggle_start:cleanup_start]
    assert toggle_body.count("self.player_screen = None") == 0
    assert toggle_body.count('self.status_bar.showMessage("Spieler-Bildschirm geschlossen")') == 0
