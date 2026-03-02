"""ImmersionTab: Soundboard (ehemals Immersion - Licht und Musik jetzt in ViewsTab)."""

from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Signal

from rpx_pro.widgets.soundboard import SoundboardWidget


class ImmersionTab(QWidget):
    """Soundboard-Tab (ehemals Immersion)."""

    status_message = Signal(str)

    def __init__(self, audio_manager):
        super().__init__()
        layout = QVBoxLayout(self)
        self.soundboard = SoundboardWidget(audio_manager)
        layout.addWidget(self.soundboard)
