#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import asyncio
from PySide6.QtWidgets import QApplication
from dotenv import load_dotenv
import os
from common.logger import get_logger
from qasync import QEventLoop, asyncSlot, run
from common.api_service import api_service
from gui.tray.tray_manager import TrayManager
from gui.modules.dashboard.dashboard_window import DashboardWindow


logger = get_logger("main")

load_dotenv()
MODE = os.getenv("MODE", "PROD")


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
        app.setQuitOnLastWindowClosed(False)
        
        loop = QEventLoop(app)
        asyncio.set_event_loop(loop)
        # # Позволяет продолжать работу при закрытии окон

        # 
        # Если нужно, можно отключить авторизацию
        if MODE == "TEST":
            logger.warning("Запущен в тестовом режиме. Не рекомендуется использовать в продакшене.")
            tray_manager = TrayManager(with_auth=False)
            dashboard = DashboardWindow()
            dashboard.show()
        else:
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