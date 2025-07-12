#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QApplication

from gui.modules.auth.auth_window import AuthWindow


# Важный аспект который нужно учитывать:
# Вызов TrayManager() должен быть в основном потоке приложения.
# Но в случае если мы не хотим что-то показывать в трее, то можно перенести в основной файл
# -------------------------------
# Это переносится в основной файл main.py
# self.auth_window = AuthWindow() 
# self.auth_window.close()
# -------------------------------
# Если вызывать и здесь и тут, то будет дублирование окон
# -------------------------------

class TrayManager:
    def __init__(self, with_auth=True):
        if not QApplication.instance():
            raise RuntimeError("QApplication must be initialized before TrayManager")

        self.auth_window = AuthWindow() if with_auth else None

        self.tray_icon = QSystemTrayIcon()
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "gui/resources", "icon.png")

        if not os.path.exists(icon_path):
            print("[TrayManager] icon.png not found, using fallback icon")
            self.tray_icon.setIcon(QIcon.fromTheme("dialog-password"))
        else:
            self.tray_icon.setIcon(QIcon(icon_path))

        self.tray_menu = QMenu()
        if with_auth:
            self.login_action = QAction("Авторизация")
            self.login_action.triggered.connect(self.show_auth_window)
            self.tray_menu.addAction(self.login_action)
            self.tray_menu.addSeparator()

        self.exit_action = QAction("Выход")
        self.exit_action.triggered.connect(self.quit_app)
        self.tray_menu.addAction(self.exit_action)

        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.activated.connect(self.on_tray_activated)
        self.tray_icon.show()

        if with_auth:
            self.show_auth_window()

    @Slot()
    def show_auth_window(self):
        if not self.auth_window:
            return
        if self.auth_window.isVisible():
            self.auth_window.activateWindow()
        else:
            self.auth_window.show()

    @Slot(QSystemTrayIcon.ActivationReason)
    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick and self.auth_window:
            self.show_auth_window()

    @Slot()
    def quit_app(self):
        self.tray_icon.hide()
        if self.auth_window:
            self.auth_window.close()
        QApplication.quit()
