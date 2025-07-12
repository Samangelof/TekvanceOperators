from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox
from PySide6.QtCore import Qt
from robots.registry import REGISTRY
from common.logger import get_logger
from gui.components.run_button import RunButton


logger = get_logger("dashboard")


class DashboardWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Главная панель")
        self.setFixedSize(300, 150)

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setAlignment(Qt.AlignTop)
        self.setCentralWidget(central)

        self.label = QLabel("Выбери робота")
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        self.selector = QComboBox()
        self.selector.addItems(REGISTRY.keys())
        layout.addWidget(self.selector)

        self.run_button = RunButton()
        self.run_button.clicked.connect(self.run_robot)
        layout.addWidget(self.run_button)

    def run_robot(self):
        name = self.selector.currentText()
        try:
            REGISTRY[name]()
            logger.success(f"Робот '{name}' запущен")
        except Exception as e:
            logger.error(f"Ошибка при запуске робота '{name}': {e}", exc_info=True)
