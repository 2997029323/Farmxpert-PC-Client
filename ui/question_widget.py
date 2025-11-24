#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
问题输入组件
支持文本输入、区域标签插入、输入历史等功能
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
                           QPushButton, QLabel, QFrame, QComboBox, QCompleter,
                           QScrollArea, QButtonGroup, QToolButton, QMenu, QAction, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal, QStringListModel
from PyQt5.QtGui import QFont, QKeySequence, QTextCursor
import re


class RegionButton(QPushButton):
    """区域按钮组件"""
    
    def __init__(self, region_id, region_name):
        super().__init__()
        self.region_id = region_id
        self.region_name = region_name
        self.setText(f"区域{region_id}")
        self.setToolTip(f"插入 <region{region_id}> 标签")
        self.setMaximumWidth(80)
        self.setMinimumHeight(32)
        self.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 12px;      /* 稍大圆角更像胶囊 */
                padding: 6px 12px;        /* 上下留足空间 */
                padding: 5px 10px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)


class QuestionTextEdit(QTextEdit):
    """自定义文本编辑器"""
    
    submit_requested = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setMaximumHeight(120)
        self.setMinimumHeight(80)
        self.setPlaceholderText("请输入您的问题...")
        
        # 设置字体
        font = QFont("Microsoft YaHei", 11)
        self.setFont(font)

        self.setObjectName("questionInput")
        # 样式设置
        self.setStyleSheet("""
                    QTextEdit#questionInput {
                        border: 2px solid #ddd;
                        border-radius: 8px;
                        padding: 10px;
                        background-color: #ffffff;
                        color: #212121;                     /* 关 键 行 */
                        selection-background-color: #3498db;
                    }
                    QTextEdit#questionInput:focus {
                        border-color: #4CAF50;
                    }
                """)
    
    def keyPressEvent(self, event):
        """处理键盘事件"""
        # Ctrl+Enter 提交
        if (event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter) and \
           event.modifiers() == Qt.ControlModifier:
            self.submit_requested.emit()
            return
        
        super().keyPressEvent(event)
    
    def insert_region_tag(self, region_id):
        """插入区域标签"""
        cursor = self.textCursor()
        tag = f"<region{region_id}>"
        cursor.insertText(tag)
        self.setTextCursor(cursor)


class QuestionInputWidget(QWidget):
    """问题输入组件"""
    
    question_submitted = pyqtSignal(str)  # 问题提交信号
    
    def __init__(self):
        super().__init__()
        self.regions = []
        self.question_history = []
        self.history_index = -1
        self.init_ui()
        self.setup_shortcuts()
    
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout()
        
        # 创建区域按钮面板
        self.create_region_buttons_panel(layout)
        
        # 创建问题输入面板
        self.create_question_input_panel(layout)
        
        # 创建控制按钮面板
        self.create_control_panel(layout)
        
        self.setLayout(layout)
    
    def create_region_buttons_panel(self, parent_layout):
        """创建区域按钮面板"""
        # 区域标签面板
        self.region_frame = QFrame()
        self.region_frame.setFrameStyle(QFrame.StyledPanel)
        # self.region_frame.setMaximumHeight(60)
        
        region_layout = QVBoxLayout()
        region_layout.setContentsMargins(12, 8, 12, 12)
        region_layout.setSpacing(6)


        # 标题
        title_layout = QHBoxLayout()
        # 标题那一行也紧凑一些
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(8)

        title_label = QLabel("区域标签:")
        title_label.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        # 帮助按钮
        help_btn = QToolButton()
        help_btn.setText("?")
        help_btn.setToolTip("点击区域按钮可在问题中插入相应的区域标签")
        help_btn.setMaximumSize(20, 20)
        title_layout.addWidget(help_btn)
        
        region_layout.addLayout(title_layout)
        
        # 区域按钮容器
        self.region_buttons_widget = QWidget()
        self.region_buttons_layout = QHBoxLayout()
        self.region_buttons_layout.setContentsMargins(0, 0, 0, 0)
        self.region_buttons_layout.setSpacing(8)
        
        # 默认提示
        self.no_regions_label = QLabel("暂无区域，请先在图像上绘制区域")
        self.no_regions_label.setStyleSheet("color: #888; font-style: italic;")
        self.region_buttons_layout.addWidget(self.no_regions_label)
        self.region_buttons_layout.addStretch()
        
        self.region_buttons_widget.setLayout(self.region_buttons_layout)
        region_layout.addWidget(self.region_buttons_widget)
        
        self.region_frame.setLayout(region_layout)
        parent_layout.addWidget(self.region_frame)
    
    def create_question_input_panel(self, parent_layout):
        """创建问题输入面板"""
        # 输入框标题
        input_title = QLabel("您的问题:")
        input_title.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        parent_layout.addWidget(input_title)
        
        # 文本输入框
        self.text_edit = QuestionTextEdit()
        self.text_edit.submit_requested.connect(self.submit_question)
        parent_layout.addWidget(self.text_edit)

        self.text_edit.setAcceptRichText(False)  # 纯文本，避免富文本带来的颜色干扰
        self.text_edit.setWordWrapMode(self.text_edit.wordWrapMode())  # 按默认方式自动换行
        # 常用问题建议
        self.create_suggestion_panel(parent_layout)
    
    def create_suggestion_panel(self, parent_layout):
        """创建建议问题面板"""
        suggestion_frame = QFrame()
        suggestion_frame.setFrameStyle(QFrame.StyledPanel)
        # suggestion_frame.setMaximumHeight(50)
        
        suggestion_layout = QVBoxLayout()
        
        # 标题
        suggestion_title = QLabel("常用问题:")
        suggestion_title.setFont(QFont("Microsoft YaHei", 9))
        suggestion_layout.addWidget(suggestion_title)
        
        # 建议按钮
        suggestions_widget = QWidget()
        suggestions_layout = QHBoxLayout()
        suggestions_layout.setContentsMargins(0, 0, 0, 0)
        
        suggestions = [
            "这张图片中有什么？",
            "请分析图片中的植物健康状况",
            "识别图片中的病虫害",
            "估算作物产量",
            "分析土壤状况"
        ]
        
        for suggestion in suggestions:
            btn = QPushButton(suggestion)
            btn.setMaximumHeight(28)
            btn.setProperty("class", "suggestion")  # ✅ 给一个 class，方便 QSS 定向
            btn.setStyleSheet("""
                    QPushButton[class="suggestion"] {
                        background-color: #f0f0f0;
                        color: #333333;                  /* 关 键 行：按钮文字设深色 */
                        border: 1px solid #ccc;
                        border-radius: 12px;
                        padding: 2px 10px;
                        font-size: 11px;
                    }
                    QPushButton[class="suggestion"]:hover {
                        background-color: #e0e0e0;
                    }
                """)
            btn.clicked.connect(lambda checked, text=suggestion: self.insert_suggestion(text))
            suggestions_layout.addWidget(btn)
        
        suggestions_layout.addStretch()
        suggestions_widget.setLayout(suggestions_layout)
        suggestion_layout.addWidget(suggestions_widget)
        
        suggestion_frame.setLayout(suggestion_layout)
        parent_layout.addWidget(suggestion_frame)
    
    def create_control_panel(self, parent_layout):
        """创建控制面板"""
        control_layout = QHBoxLayout()
        
        # 历史记录按钮
        self.history_btn = QPushButton("历史问题")
        self.history_btn.setEnabled(False)
        self.history_btn.clicked.connect(self.show_history_menu)
        
        # 清空按钮
        self.clear_btn = QPushButton("清空")
        self.clear_btn.clicked.connect(self.clear_input)
        
        # 提交按钮
        self.submit_btn = QPushButton("提交问题")
        self.submit_btn.setDefault(True)
        self.submit_btn.clicked.connect(self.submit_question)
        self.submit_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        
        control_layout.addWidget(self.history_btn)
        control_layout.addWidget(self.clear_btn)
        control_layout.addStretch()
        control_layout.addWidget(self.submit_btn)
        
        parent_layout.addLayout(control_layout)
    
    def setup_shortcuts(self):
        """设置快捷键"""
        # Ctrl+Enter 提交
        # 已在 QuestionTextEdit 中处理
        pass
    
    def update_regions(self, regions):
        """更新区域信息"""
        self.regions = regions
        self.update_region_buttons()
    
    def update_region_buttons(self):
        """更新区域按钮"""
        # 清空现有按钮
        while self.region_buttons_layout.count():
            child = self.region_buttons_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        if not self.regions:
            # 显示无区域提示
            self.no_regions_label = QLabel("暂无区域，请先在图像上绘制区域")
            self.no_regions_label.setStyleSheet("color: #888; font-style: italic;")
            self.region_buttons_layout.addWidget(self.no_regions_label)
        else:
            # 添加区域按钮
            for region in self.regions:
                region_id = region['id']
                region_name = region['name']
                
                btn = RegionButton(region_id, region_name)
                btn.clicked.connect(
                    lambda checked, rid=region_id: self.insert_region_tag(rid)
                )
                self.region_buttons_layout.addWidget(btn)
        
        self.region_buttons_layout.addStretch()
    
    def insert_region_tag(self, region_id):
        """插入区域标签"""
        self.text_edit.insert_region_tag(region_id)
        self.text_edit.setFocus()
    
    def insert_suggestion(self, suggestion_text):
        """插入建议问题"""
        self.text_edit.setPlainText(suggestion_text)
        self.text_edit.setFocus()
        
        # 移动光标到末尾
        cursor = self.text_edit.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.text_edit.setTextCursor(cursor)
    
    def submit_question(self):
        """提交问题"""
        question = self.text_edit.toPlainText().strip()
        
        if not question:
            self.text_edit.setFocus()
            return
        
        # 添加到历史记录
        if question not in self.question_history:
            self.question_history.append(question)
            if len(self.question_history) > 20:  # 限制历史记录数量
                self.question_history.pop(0)
        
        # 更新历史按钮状态
        self.history_btn.setEnabled(len(self.question_history) > 0)
        
        # 发送信号
        self.question_submitted.emit(question)
    
    def show_history_menu(self):
        """显示历史问题菜单"""
        if not self.question_history:
            return
        
        menu = QMenu(self)
        
        # 添加最近的10个问题
        recent_questions = self.question_history[-10:]
        for question in reversed(recent_questions):
            # 限制显示长度
            display_text = question if len(question) <= 50 else question[:47] + "..."
            action = QAction(display_text, self)
            action.triggered.connect(
                lambda checked, q=question: self.load_history_question(q)
            )
            menu.addAction(action)
        
        # 在按钮下方显示菜单
        menu.exec_(self.history_btn.mapToGlobal(
            self.history_btn.rect().bottomLeft()
        ))
    
    def load_history_question(self, question):
        """加载历史问题"""
        self.text_edit.setPlainText(question)
        self.text_edit.setFocus()
        
        # 移动光标到末尾
        cursor = self.text_edit.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.text_edit.setTextCursor(cursor)
    
    def clear_input(self):
        """清空输入"""
        self.text_edit.clear()
        self.text_edit.setFocus()
    
    def get_current_question(self):
        """获取当前问题"""
        return self.text_edit.toPlainText().strip()
    
    def set_enabled(self, enabled):
        """设置组件启用状态"""
        super().setEnabled(enabled)
        self.text_edit.setEnabled(enabled)
        self.submit_btn.setEnabled(enabled)
    
    def validate_question(self, question):
        """验证问题格式"""
        # 检查区域标签格式
        region_pattern = r'<region(\d+)>'
        region_matches = re.findall(region_pattern, question)
        
        # 检查引用的区域是否存在
        region_ids = [region['id'] for region in self.regions]
        for match in region_matches:
            region_id = int(match)
            if region_id not in region_ids:
                return False, f"引用的区域{region_id}不存在"
        
        return True, ""