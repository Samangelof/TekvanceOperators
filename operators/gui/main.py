#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import asyncio
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QEventLoop, QTimer
# from gui.auth.auth_window import AuthWindow
from common.logger import get_logger
from common.api_service import api_service
from gui.tray.tray_manager import TrayManager
from qasync import QEventLoop


logger = get_logger("main")

# -- Для интеграции asyncio с Qt --
class QEventLoopPolicy(asyncio.AbstractEventLoopPolicy):
    def __init__(self):
        self._event_loop = None

    def get_event_loop(self):
        if self._event_loop is None:
            self._event_loop = QEventLoop()
        return self._event_loop

    def set_event_loop(self, loop):
        self._event_loop = loop

    def new_event_loop(self):
        return QEventLoop()

def run_gui():
    """Основная функция приложения"""
    try:
        # Инициализация приложения Qt
        app = QApplication(sys.argv)
        loop = QEventLoop(app)
        asyncio.set_event_loop(loop)
        # # Позволяет продолжать работу при закрытии окон
        # app.setQuitOnLastWindowClosed(False)

        tray_manager = TrayManager()


        # Настройка asyncio для работы с Qt
        with loop:
            loop.run_forever()
        
        
        # -- см. TrayManager --
        # auth_window = AuthWindow()
        # auth_window.show()
        # ---------------------

        # Запуск главного цикла приложения
        exit_code = app.exec()
        
        # Закрытие API-сессии перед выходом
        loop = asyncio.get_event_loop()
        loop.run_until_complete(api_service.close())
        
        sys.exit(exit_code)
        
    except Exception as e:
        logger.error(f"Ошибка при запуске приложения: {e}", exc_info=True)
        sys.exit(1)