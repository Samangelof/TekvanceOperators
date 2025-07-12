#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Стили для полей формы (input, textarea и т.д.)
FORM_STYLE = """
    QLineEdit {
        border: 1px solid #ccc;
        border-radius: 4px;
        padding: 6px;
        font-size: 14px;
        background-color: #f8f8f8;
    }
    QLineEdit:focus {
        border: 1px solid #0078d7;
        background-color: #fff;
    }
"""

# Стиль для кнопок
BUTTON_STYLE = """
    QPushButton {
        padding: 8px 16px;
        background-color: #0078d7;
        color: white;
        border: none;
        border-radius: 4px;
        font-size: 12px;
        font-weight: bold;
    }
    
    QPushButton:hover {
        background-color: #0063b1;
    }
    
    QPushButton:pressed {
        background-color: #004c8c;
    }
    
    QPushButton:disabled {
        background-color: #cccccc;
        color: #666666;
    }
"""


ERROR_STYLE = """
    QLabel {
        color: #d32f2f;
        font-size: 12px;
        padding: 5px;
    }
"""