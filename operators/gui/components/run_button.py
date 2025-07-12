from PySide6.QtWidgets import QPushButton


class RunButton(QPushButton):
    def __init__(self, label="▶ Запуск", parent=None):
        super().__init__(label, parent)
        self.setFixedHeight(40)
        self.setStyleSheet("""
            QPushButton {
                font-weight: bold;
                font-size: 14px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3e8e41;
            }
        """)
