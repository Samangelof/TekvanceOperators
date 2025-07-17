#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QApplication

from gui.modules.auth.auth_window import AuthWindow
from gui.modules.dashboard.dashboard_window import DashboardWindow


# Важный аспект который нужно учитывать:
# Вызов TrayManager() должен быть в основном потоке приложения.
# Но в случае если мы не хотим что-то показывать в трее, то можно перенести в основной файл
# -------------------------------
# Это переносится в основной файл main.py
# self.auth_window = AuthWindow() 
# self.auth_window.close()
# -------------------------------
# Если вызывать и здесь и там, то будет дублирование окон
# -------------------------------

class TrayManager:
    def __init__(self, with_auth=True):
        if not QApplication.instance():
            raise RuntimeError("QApplication must be initialized before TrayManager")

        self.auth_window = AuthWindow() if with_auth else None
        self.dashboard = None
        self.authorized = False

        self.tray_icon = QSystemTrayIcon()
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "gui/resources", "icon.png")
        self.tray_icon.setIcon(QIcon(icon_path) if os.path.exists(icon_path) else QIcon.fromTheme("dialog-password"))
        self.tray_icon.setToolTip("Tekvance Agent")

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
            self.auth_window.login_successful.connect(self.on_login_success)

    @Slot()
    def show_auth_window(self):
        if not self.auth_window:
            return
        if self.auth_window.isVisible():
            self.auth_window.activateWindow()
        else:
            self.auth_window.show()

    @Slot()
    def show_dashboard(self):
        if self.dashboard is None:
            self.dashboard = DashboardWindow()
        if self.dashboard.isVisible():
            self.dashboard.activateWindow()
        else:
            self.dashboard.show()

    @Slot()
    def on_login_success(self):
        self.authorized = True
        if self.auth_window:
            self.auth_window.close()
            self.tray_menu.removeAction(self.login_action)
            self.login_action = None
        self.show_dashboard()



    @Slot(QSystemTrayIcon.ActivationReason)
    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            if self.authorized:
                self.show_dashboard()
            else:
                self.show_auth_window()

    @Slot()
    def quit_app(self):
        self.tray_icon.hide()
        if self.auth_window:
            self.auth_window.close()
        if self.dashboard:
            self.dashboard.close()
        QApplication.quit()