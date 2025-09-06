# gui/modules/auth/auth_window.py
from PySide6.QtWidgets import QDialog
from PySide6.QtCore import Signal
from qasync import asyncSlot

from .auth_ui import Ui_AuthDialog
from .controller import AuthController
from .styles import FORM_STYLE, BUTTON_STYLE, ERROR_STYLE
from common.logger import get_logger

logger = get_logger("auth")


class AuthWindow(QDialog, Ui_AuthDialog):
    """Окно авторизации пользователя"""
    login_successful = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.controller = AuthController()

        # стили
        self.loginLineEdit.setStyleSheet(FORM_STYLE)
        self.passwordLineEdit.setStyleSheet(FORM_STYLE)
        self.loginButton.setStyleSheet(BUTTON_STYLE)

        # error label можно добавить прямо в .ui
        if hasattr(self, "errorLabel"):
            self.errorLabel.setStyleSheet(ERROR_STYLE)
            self.errorLabel.setVisible(False)

        # бинды
        self.loginButton.clicked.connect(self.on_login)
        self.loginLineEdit.returnPressed.connect(self.on_login)
        self.passwordLineEdit.returnPressed.connect(self.on_login)

    @asyncSlot()
    async def on_login(self):
        """Обработка входа"""
        login = self.loginLineEdit.text().strip()
        password = self.passwordLineEdit.text().strip()

        if not login or not password:
            self.show_error("Введите логин и пароль")
            return

        self.block_ui(True)
        logger.debug(f"[Auth] Проверка логина: {login}")

        try:
            ok, msg = await self.controller.login(login, password)
            if ok:
                logger.success("[Auth] Авторизация успешна")
                self.login_successful.emit()
                self.accept()  # закрыть с кодом успеха
            else:
                self.show_error(msg or "Ошибка аутентификации")
                logger.error(f"[Auth] Ошибка: {msg}")
        except Exception as e:
            self.show_error("Системная ошибка, см. логи")
            logger.error(f"[Auth] Exception: {e}", exc_info=True)
        finally:
            self.block_ui(False)

    def show_error(self, message: str):
        """Показ ошибки в форме"""
        if hasattr(self, "errorLabel"):
            self.errorLabel.setText(message)
            self.errorLabel.setVisible(True)
        else:
            logger.warning(f"[Auth] Ошибка без errorLabel: {message}")

    def block_ui(self, status: bool):
        """Блокировка элементов на время проверки"""
        self.loginButton.setEnabled(not status)
        self.loginButton.setText("Проверка..." if status else "Войти")
        self.loginLineEdit.setEnabled(not status)
        self.passwordLineEdit.setEnabled(not status)
