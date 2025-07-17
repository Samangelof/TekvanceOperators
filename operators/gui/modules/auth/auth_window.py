#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLineEdit, QPushButton, QLabel, QFormLayout
)
from qasync import asyncSlot
from PySide6.QtCore import Qt, Signal
from common.logger import get_logger
from gui.modules.auth.styles import FORM_STYLE, BUTTON_STYLE, ERROR_STYLE
from gui.modules.auth.controller import AuthController
from gui.modules.dashboard.dashboard_window import DashboardWindow


logger = get_logger("auth")



class AuthWindow(QMainWindow):
    """Окно авторизации пользователя"""
    login_successful = Signal()
    
    def __init__(self):
        super().__init__()
        self.controller = AuthController()

        # Настройка окна
        self.setWindowTitle("Авторизация")
        self.setFixedSize(350, 200)
        
        # Создаем центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Главная вертикальная компоновка
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Заголовок
        title_label = QLabel("Вход в систему")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        main_layout.addWidget(title_label)
        

        # # Сообщение об ошибке (изначально скрыто)
        # self.error_label = QLabel("")
        # self.error_label.setStyleSheet(ERROR_STYLE)
        # self.error_label.setAlignment(Qt.AlignCenter)
        # self.error_label.setWordWrap(True)
        # self.error_label.setVisible(False)
        # main_layout.addWidget(self.error_label)


        # Форма авторизации
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        # Поле логина
        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Введите логин")
        self.login_input.setStyleSheet(FORM_STYLE)
        form_layout.addRow("Логин:", self.login_input)
        
        # Поле пароля
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Введите пароль")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet(FORM_STYLE)
        form_layout.addRow("Пароль:", self.password_input)
        
        main_layout.addLayout(form_layout)
        
        # Кнопки
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # Кнопка входа
        self.login_button = QPushButton("Войти")
        self.login_button.setStyleSheet(BUTTON_STYLE)
        self.login_button.clicked.connect(self.on_login)
        button_layout.addWidget(self.login_button)
        
        main_layout.addLayout(button_layout)
        
        # Обработка нажатия Enter
        self.login_input.returnPressed.connect(self.on_login)
        self.password_input.returnPressed.connect(self.on_login)
    
    @asyncSlot()
    async def on_login(self):
        """Обработка нажатия кнопки Войти"""
        login = self.login_input.text()
        password = self.password_input.text()
        
        # # Проверка наличия данных
        # if not login or not password:
        #     self.show_error("Введите логин и пароль")
        #     return
        
        # Отключаем кнопку на время проверки
        self.login_button.setEnabled(False)
        self.login_button.setText("Проверка...")
        logger.debug(f"Проверка логина: {login}")

        # Скрываем сообщение об ошибке
        # self.error_label.setVisible(False)
        
        # Запускаем асинхронную проверку
        await self.perform_login(login, password)

    
    async def perform_login(self, login: str, password: str):
        logger.debug(f'[perform_login] Запускаем проверку для {login}')
        try:
            ok, msg = await self.controller.login(login, password)
            if ok:
                logger.success("Авторизация и верификация успешны")
                self.login_successful.emit()
                #? ---
                #? login_successful.emit() передаест сигнал в TrayManager об успешной авторизации
                #? И создаст DashboardWindow
                #? ---
                # self.main_window = DashboardWindow()
                # self.main_window.show()
                self.close()
            else:
                logger.error(f"Ошибка аутентификации: {msg}")
        except Exception as e:
            logger.error(f"Ошибка при авторизации: {e}", exc_info=True)
        finally:
            self.login_button.setEnabled(True)
            self.login_button.setText("Войти")
            self.password_input.clear()

    
    # def show_error(self, message: str):
    #     """Показывает сообщение об ошибке"""
    #     self.error_label.setText(message)
    #     self.error_label.setVisible(True)