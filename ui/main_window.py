#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主窗口模块
整合所有功能组件
"""

from PyQt5.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                             QSplitter, QMenuBar, QAction, QStatusBar, QToolBar,
                             QMessageBox, QProgressBar, QLabel)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QIcon, QKeySequence
import os

from .image_widget import ImageWidget
from .drawing_widget import RegionDrawingWidget
from .question_widget import QuestionInputWidget
from .chat_widget import ChatHistoryWidget
from core.model_manager import ModelManager


class MainWindow(QMainWindow):
    """主窗口类"""

    def __init__(self):
        super().__init__()
        self.model_manager = ModelManager()
        self.init_ui()
        self.connect_signals()
        self.setup_status_bar()

    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("农业视觉问答助手 v1.0")
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1200, 800)

        # 创建中央组件
        self.setup_central_widget()

        # 创建菜单栏
        self.setup_menu_bar()

        # 创建工具栏
        self.setup_tool_bar()

        # 设置窗口图标
        if os.path.exists("resources/icons/app_icon.png"):
            self.setWindowIcon(QIcon("resources/icons/app_icon.png"))

    def setup_central_widget(self):
        """设置中央组件布局"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主水平分割器
        main_splitter = QSplitter(Qt.Horizontal)

        # 左侧面板：图像和绘制区域
        left_panel = self.create_left_panel()

        # 右侧面板：问答区域
        right_panel = self.create_right_panel()

        # 添加到分割器
        main_splitter.addWidget(left_panel)
        main_splitter.addWidget(right_panel)
        main_splitter.setSizes([800, 600])  # 设置初始比例

        # 设置中央布局
        layout = QHBoxLayout()
        layout.addWidget(main_splitter)
        layout.setContentsMargins(5, 5, 5, 5)
        central_widget.setLayout(layout)

    def create_left_panel(self):
        """创建左侧面板"""
        left_widget = QWidget()
        left_layout = QVBoxLayout()

        # 图像显示组件
        self.image_widget = ImageWidget()

        # 区域绘制组件
        self.drawing_widget = RegionDrawingWidget()

        # 垂直分割器
        left_splitter = QSplitter(Qt.Vertical)
        left_splitter.addWidget(self.image_widget)
        left_splitter.addWidget(self.drawing_widget)
        left_splitter.setSizes([600, 200])

        left_layout.addWidget(left_splitter)
        left_widget.setLayout(left_layout)

        return left_widget

    def create_right_panel(self):
        """创建右侧面板"""
        right_widget = QWidget()
        right_layout = QVBoxLayout()

        # 对话历史组件
        self.chat_widget = ChatHistoryWidget()

        # 问题输入组件
        self.question_widget = QuestionInputWidget()

        # 垂直分割器
        right_splitter = QSplitter(Qt.Vertical)
        right_splitter.addWidget(self.chat_widget)
        right_splitter.addWidget(self.question_widget)
        right_splitter.setSizes([600, 150])

        right_layout.addWidget(right_splitter)
        right_widget.setLayout(right_layout)

        return right_widget

    def setup_menu_bar(self):
        """设置菜单栏"""
        menubar = self.menuBar()

        # 文件菜单
        file_menu = menubar.addMenu('文件(&F)')

        # 打开图像
        open_action = QAction('打开图像(&O)', self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.setStatusTip('打开图像文件')
        open_action.triggered.connect(self.image_widget.open_image)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        # 退出
        exit_action = QAction('退出(&X)', self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.setStatusTip('退出应用程序')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # 编辑菜单
        edit_menu = menubar.addMenu('编辑(&E)')

        # 清空区域
        clear_regions_action = QAction('清空区域(&C)', self)
        clear_regions_action.setShortcut('Ctrl+Shift+C')
        clear_regions_action.setStatusTip('清空所有绘制的区域')
        clear_regions_action.triggered.connect(self.drawing_widget.clear_all_regions)
        edit_menu.addAction(clear_regions_action)

        # 清空对话
        clear_chat_action = QAction('清空对话(&H)', self)
        clear_chat_action.setShortcut('Ctrl+Shift+H')
        clear_chat_action.setStatusTip('清空对话历史')
        clear_chat_action.triggered.connect(self.chat_widget.clear_history)
        edit_menu.addAction(clear_chat_action)

        # 帮助菜单
        help_menu = menubar.addMenu('帮助(&H)')

        # 关于
        about_action = QAction('关于(&A)', self)
        about_action.setStatusTip('关于应用程序')
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def setup_tool_bar(self):
        """设置工具栏"""
        toolbar = QToolBar("主工具栏")
        self.addToolBar(toolbar)

        # 打开图像
        open_action = QAction('打开图像', self)
        if os.path.exists("resources/icons/open.png"):
            open_action.setIcon(QIcon("resources/icons/open.png"))
        open_action.triggered.connect(self.image_widget.open_image)
        toolbar.addAction(open_action)

        toolbar.addSeparator()

        # 清空区域
        clear_regions_action = QAction('清空区域', self)
        if os.path.exists("resources/icons/clear.png"):
            clear_regions_action.setIcon(QIcon("resources/icons/clear.png"))
        clear_regions_action.triggered.connect(self.drawing_widget.clear_all_regions)
        toolbar.addAction(clear_regions_action)

        # 清空对话
        clear_chat_action = QAction('清空对话', self)
        if os.path.exists("resources/icons/chat_clear.png"):
            clear_chat_action.setIcon(QIcon("resources/icons/chat_clear.png"))
        clear_chat_action.triggered.connect(self.chat_widget.clear_history)
        toolbar.addAction(clear_chat_action)

    def setup_status_bar(self):
        """设置状态栏"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # 状态标签
        self.status_label = QLabel("就绪")
        self.status_bar.addWidget(self.status_label)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)

        # 模型状态标签
        self.model_status_label = QLabel("模型未加载")
        self.status_bar.addPermanentWidget(self.model_status_label)

    def connect_signals(self):
        """连接信号和槽"""
        # 图像加载完成后，传递给绘制组件
        self.image_widget.image_loaded.connect(self.drawing_widget.set_image)

        # 问题提交信号
        self.question_widget.question_submitted.connect(self.handle_question)

        # 区域变化信号
        self.drawing_widget.regions_changed.connect(self.update_region_info)

        # 模型状态信号
        self.model_manager.model_loaded.connect(self.on_model_loaded)
        self.model_manager.inference_started.connect(self.on_inference_started)
        self.model_manager.inference_finished.connect(self.on_inference_finished)
        self.model_manager.error_occurred.connect(self.on_error_occurred)

    def handle_question(self, question):
        """处理用户问题"""
        if not self.image_widget.current_image:
            QMessageBox.warning(self, "警告", "请先上传图像！")
            return

        # 获取当前区域
        regions = self.drawing_widget.get_regions()

        # 添加用户消息到聊天历史
        self.chat_widget.add_user_message(question)

        # 开始推理
        self.model_manager.process_question(
            question,
            self.image_widget.current_image,
            regions
        )

    def update_region_info(self, regions):
        """更新区域信息"""
        region_count = len(regions)
        self.status_label.setText(f"已绘制 {region_count} 个区域")

        # 更新问题输入组件的区域信息
        self.question_widget.update_regions(regions)

    def on_model_loaded(self):
        """模型加载完成"""
        self.model_status_label.setText("模型已就绪")
        self.status_label.setText("模型加载完成，可以开始问答")

    def on_inference_started(self):
        """推理开始"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 不确定进度
        self.status_label.setText("正在生成回答...")
        self.question_widget.setEnabled(False)

    def on_inference_finished(self, answer):
        """推理完成"""
        self.progress_bar.setVisible(False)
        self.status_label.setText("回答生成完成")
        self.question_widget.setEnabled(True)

        # 添加助手回复到聊天历史
        self.chat_widget.add_assistant_message(answer)

        # 清空问题输入框
        self.question_widget.clear_input()

    def on_error_occurred(self, error_msg):
        """处理错误"""
        self.progress_bar.setVisible(False)
        self.status_label.setText("发生错误")
        self.question_widget.setEnabled(True)

        QMessageBox.critical(self, "错误", f"处理过程中发生错误：\n{error_msg}")

    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self,
            "关于",
            "农业视觉问答助手 v1.0\n\n"
            "基于先进的多模态大语言模型\n"
            "为农业应用提供智能视觉问答服务\n\n"
            "开发团队：农业AI实验室"
        )

    def closeEvent(self, event):
        """关闭事件处理"""
        reply = QMessageBox.question(
            self,
            '确认退出',
            '确定要退出应用程序吗？',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # 清理资源
            self.model_manager.cleanup()
            event.accept()
        else:
            event.ignore()