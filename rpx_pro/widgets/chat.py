"""ChatWidget: Chat-Widget mit Farbcodierung nach Rolle."""

from datetime import datetime
from typing import List

from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame,
    QLabel, QComboBox, QLineEdit, QTextEdit, QTextBrowser, QPushButton,
)

from rpx_pro.models.enums import MessageRole
from rpx_pro.models.session import ChatMessage


class ChatWidget(QWidget):
    """Chat-Widget mit Farbcodierung nach Rolle"""

    message_sent = Signal(ChatMessage)

    ROLE_COLORS = {
        MessageRole.PLAYER: "#3498db",
        MessageRole.GM: "#e74c3c",
        MessageRole.AI_STORYTELLER: "#9b59b6",
        MessageRole.AI_WORLD_DESIGNER: "#27ae60",
        MessageRole.AI_NPC: "#e67e22",
        MessageRole.AI_PLOTTWIST: "#f39c12",
        MessageRole.AI_ENEMY: "#c0392b",
        MessageRole.AI_LANDSCAPE: "#16a085",
        MessageRole.AI_FAUNA_FLORA: "#2ecc71",
        MessageRole.SYSTEM: "#7f8c8d",
        MessageRole.NARRATOR: "#1abc9c",
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        self.chat_display = QTextBrowser()
        self.chat_display.setOpenExternalLinks(False)
        self.chat_display.setStyleSheet("""
            QTextBrowser {
                background-color: #1a1a2e;
                color: #eee;
                border: 1px solid #333;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Segoe UI', sans-serif;
                font-size: 13px;
            }
        """)
        layout.addWidget(self.chat_display, stretch=1)

        input_frame = QFrame()
        input_frame.setStyleSheet("background-color: #16213e; border-radius: 5px; padding: 5px;")
        input_layout = QVBoxLayout(input_frame)

        role_layout = QHBoxLayout()
        role_layout.addWidget(QLabel("Rolle:"))
        self.role_combo = QComboBox()
        for role in MessageRole:
            self.role_combo.addItem(role.value.replace("_", " ").title(), role)
        self.role_combo.setCurrentIndex(0)
        role_layout.addWidget(self.role_combo)

        role_layout.addWidget(QLabel("Name:"))
        self.author_input = QLineEdit()
        self.author_input.setPlaceholderText("Dein Name...")
        role_layout.addWidget(self.author_input)

        input_layout.addLayout(role_layout)

        msg_layout = QHBoxLayout()
        self.message_input = QTextEdit()
        self.message_input.setMaximumHeight(80)
        self.message_input.setPlaceholderText("Nachricht eingeben...")
        msg_layout.addWidget(self.message_input)

        self.send_button = QPushButton("Senden")
        self.send_button.setMinimumHeight(60)
        self.send_button.clicked.connect(self.send_message)
        msg_layout.addWidget(self.send_button)

        input_layout.addLayout(msg_layout)
        layout.addWidget(input_frame)

    def add_message(self, message: ChatMessage):
        """Fuegt eine Nachricht zum Chat hinzu"""
        color = self.ROLE_COLORS.get(message.role, "#aaa")
        timestamp = datetime.fromtimestamp(message.timestamp).strftime("%H:%M")
        role_name = message.role.value.replace("_", " ").title()

        html = f'''
        <div style="margin-bottom: 10px; padding: 8px; background-color: rgba(255,255,255,0.05); border-radius: 5px; border-left: 3px solid {color};">
            <span style="color: {color}; font-weight: bold;">[{role_name}]</span>
            <span style="color: #888; font-size: 11px;">{timestamp}</span>
            <span style="color: {color}; font-weight: bold;"> {message.author}:</span>
            <div style="color: #eee; margin-top: 5px; padding-left: 10px;">{message.content}</div>
        </div>
        '''

        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.chat_display.setTextCursor(cursor)
        self.chat_display.insertHtml(html)
        self.chat_display.ensureCursorVisible()

    def send_message(self):
        """Sendet die aktuelle Nachricht"""
        content = self.message_input.toPlainText().strip()
        if not content:
            return

        role = self.role_combo.currentData()
        author = self.author_input.text().strip() or "Anonym"

        message = ChatMessage(role=role, author=author, content=content)
        self.add_message(message)
        self.message_sent.emit(message)

        self.message_input.clear()

    def load_history(self, messages: List[ChatMessage]):
        """Laedt Chat-Verlauf"""
        self.chat_display.clear()
        for msg in messages:
            self.add_message(msg)
