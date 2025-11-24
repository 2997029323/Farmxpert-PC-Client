#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
农业视觉问答大模型应用
主程序入口
"""

import sys, platform
from pathlib import Path
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFont
from PyQt5 import QtCore, QtWidgets
from ui.main_window import MainWindow

def load_styles(app):
    qss_path = Path(__file__).with_name("styles.css")  # 确保 styles.css 和 main.py 同目录
    if qss_path.exists():
        app.setStyleSheet(qss_path.read_text(encoding="utf-8"))
    else:
        print("未找到样式文件，使用默认样式")

def main():
    """主函数"""
    # 创建应用程序

    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
    app = QApplication(sys.argv)
    family = "PingFang SC" if platform.system() == "Darwin" else "Microsoft YaHei"
    app.setFont(QFont(family, 10))
    load_styles(app)
    app.setApplicationName("农业视觉问答助手")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("农业AI实验室")

    # 设置应用程序图标
    if os.path.exists("resources/icons/app_icon.png"):
        app.setWindowIcon(QIcon("resources/icons/app_icon.png"))

    # 设置全局字体
    font = QFont("Microsoft YaHei", 10)
    app.setFont(font)

    # 启用高DPI支持
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    # 加载全局样式
    try:
        with open("resources/styles.qss", "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        print("未找到样式文件，使用默认样式")

    # 创建主窗口
    window = MainWindow()
    window.show()

    # 运行应用程序
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()