#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import asyncio
import logging
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QEventLoop
# from gui.auth.auth_window import AuthWindow
from operators.common.api_service import api_service
from gui.tray.tray_manager import TrayManager
from qasync import QEventLoop, asyncSlot


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)

logger = logging.getLogger(__name__)

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

        async def on_exit():
            await api_service.close()

        app.aboutToQuit.connect(lambda: loop.create_task(on_exit()))

        # Настройка asyncio для работы с Qt
        with loop:
            exit_code = app.exec()

    
        # -- см. TrayManager --
        # auth_window = AuthWindow()
        # auth_window.show()
        # ---------------------
        
        sys.exit(exit_code)
        
    except Exception as e:
        logger.error(f"Ошибка при запуске приложения: {e}", exc_info=True)
        sys.exit(1)
