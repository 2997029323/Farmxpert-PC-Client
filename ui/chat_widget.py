#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
对话历史组件
显示用户和AI助手的对话历史
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, 
                           QLabel, QFrame, QPushButton, QTextEdit, QSizePolicy)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QPixmap, QPainter, QPainterPath, QColor, QBrush
import datetime
import os


class MessageBubble(QFrame):
    """消息气泡组件"""
    
    def __init__(self, message, is_user=True, timestamp=None):
        super().__init__()
        self.message = message
        self.is_user = is_user
        self.timestamp = timestamp or datetime.datetime.now()
        self.init_ui()
    
    def init_ui(self):
        """初始化用户界面"""
        self.setMaximumWidth(600)
        
        # 设置气泡样式
        if self.is_user:
            self.setStyleSheet("""
                QFrame {
                    background-color: #4CAF50;
                    border-radius: 15px;
                    margin: 5px;
                    padding: 10px;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: #f1f1f1;
                    border-radius: 15px;
                    margin: 5px;
                    padding: 10px;
                }
            """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 10, 15, 10)
        
        # 消息文本
        message_label = QLabel(self.message)
        message_label.setWordWrap(True)
        message_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        
        # 设置字体和颜色
        font = QFont("Microsoft YaHei", 11)
        message_label.setFont(font)
        
        if self.is_user:
            message_label.setStyleSheet("color: white; line-height: 1.4;")
        else:
            message_label.setStyleSheet("color: #333; line-height: 1.4;")
        
        layout.addWidget(message_label)
        
        # 时间戳
        time_label = QLabel(self.timestamp.strftime("%H:%M"))
        time_label.setFont(QFont("Microsoft YaHei", 9))
        
        if self.is_user:
            time_label.setStyleSheet("color: rgba(255, 255, 255, 0.8);")
            time_label.setAlignment(Qt.AlignRight)
        else:
            time_label.setStyleSheet("color: #888;")
            time_label.setAlignment(Qt.AlignLeft)
        
        layout.addWidget(time_label)
        
        self.setLayout(layout)


class AvatarLabel(QLabel):
    """头像标签"""
    
    def __init__(self, is_user=True):
        super().__init__()
        self.is_user = is_user
        self.setFixedSize(40, 40)
        self.load_avatar()
    
    def load_avatar(self):
        """加载头像"""
        if self.is_user:
            avatar_path = "resources/avatars/user.png"
            default_color = QColor(52, 152, 219)  # 蓝色
            text = "用"
        else:
            avatar_path = "resources/avatars/assistant.png"
            default_color = QColor(46, 125, 50)  # 绿色
            text = "AI"
        
        if os.path.exists(avatar_path):
            pixmap = QPixmap(avatar_path)
            # 创建圆形头像
            self.setPixmap(self.create_circular_pixmap(pixmap))
        else:
            # 使用默认头像
            self.create_default_avatar(default_color, text)
    
    def create_circular_pixmap(self, pixmap):
        """创建圆形头像"""
        size = min(pixmap.width(), pixmap.height())
        circular_pixmap = QPixmap(self.size())
        circular_pixmap.fill(Qt.transparent)
        
        painter = QPainter(circular_pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 创建圆形路径
        path = QPainterPath()
        path.addEllipse(0, 0, self.width(), self.height())
        painter.setClipPath(path)
        
        # 绘制缩放后的图像
        scaled_pixmap = pixmap.scaled(
            self.size(), 
            Qt.KeepAspectRatioByExpanding, 
            Qt.SmoothTransformation
        )
        painter.drawPixmap(0, 0, scaled_pixmap)
        painter.end()
        
        return circular_pixmap
    
    def create_default_avatar(self, color, text):
        """创建默认头像"""
        pixmap = QPixmap(self.size())
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 绘制圆形背景
        painter.setBrush(QBrush(color))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, self.width(), self.height())
        
        # 绘制文字
        painter.setPen(QColor(255, 255, 255))
        font = QFont("Microsoft YaHei", 12, QFont.Bold)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignCenter, text)
        painter.end()
        
        self.setPixmap(pixmap)


class MessageContainer(QWidget):
    """消息容器"""
    
    def __init__(self, message, is_user=True, timestamp=None):
        super().__init__()
        self.message = message
        self.is_user = is_user
        self.timestamp = timestamp
        self.init_ui()
    
    def init_ui(self):
        """初始化用户界面"""
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)
        
        if self.is_user:
            # 用户消息：右对齐
            layout.addStretch()
            
            # 消息气泡
            bubble = MessageBubble(self.message, True, self.timestamp)
            layout.addWidget(bubble)
            
            # 用户头像
            avatar = AvatarLabel(True)
            layout.addWidget(avatar)
            
        else:
            # 助手消息：左对齐
            # 助手头像
            avatar = AvatarLabel(False)
            layout.addWidget(avatar)
            
            # 消息气泡
            bubble = MessageBubble(self.message, False, self.timestamp)
            layout.addWidget(bubble)
            
            layout.addStretch()
        
        self.setLayout(layout)


class TypingIndicator(QWidget):
    """打字指示器"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.setup_animation()
    
    def init_ui(self):
        """初始化用户界面"""
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)
        
        # 助手头像
        avatar = AvatarLabel(False)
        layout.addWidget(avatar)
        
        # 打字指示器
        typing_frame = QFrame()
        typing_frame.setMaximumWidth(100)
        typing_frame.setStyleSheet("""
            QFrame {
                background-color: #f1f1f1;
                border-radius: 15px;
                margin: 5px;
                padding: 15px;
            }
        """)
        
        typing_layout = QHBoxLayout()
        typing_layout.setContentsMargins(10, 5, 10, 5)
        
        # 三个点
        self.dots = []
        for i in range(3):
            dot = QLabel("●")
            dot.setStyleSheet("color: #888; font-size: 16px;")
            dot.setAlignment(Qt.AlignCenter)
            self.dots.append(dot)
            typing_layout.addWidget(dot)
        
        typing_frame.setLayout(typing_layout)
        layout.addWidget(typing_frame)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def setup_animation(self):
        """设置动画"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate_dots)
        self.animation_step = 0
    
    def start_animation(self):
        """开始动画"""
        self.timer.start(500)  # 每500ms切换一次
    
    def stop_animation(self):
        """停止动画"""
        self.timer.stop()
        # 重置所有点的颜色
        for dot in self.dots:
            dot.setStyleSheet("color: #888; font-size: 16px;")
    
    def animate_dots(self):
        """动画效果"""
        # 重置所有点
        for dot in self.dots:
            dot.setStyleSheet("color: #888; font-size: 16px;")
        
        # 高亮当前点
        if self.animation_step < len(self.dots):
            self.dots[self.animation_step].setStyleSheet("color: #4CAF50; font-size: 16px;")
        
        self.animation_step = (self.animation_step + 1) % (len(self.dots) + 1)


class ChatHistoryWidget(QWidget):
    """对话历史组件"""
    
    def __init__(self):
        super().__init__()
        self.messages = []
        self.typing_indicator = None
        self.init_ui()
    
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        
        # 标题栏
        header = self.create_header()
        layout.addWidget(header)
        
        # 消息显示区域
        self.create_message_area(layout)
        
        self.setLayout(layout)
    
    def create_header(self):
        """创建标题栏"""
        header = QFrame()
        header.setFrameStyle(QFrame.StyledPanel)
        header.setMaximumHeight(50)
        
        layout = QHBoxLayout()
        
        # 标题
        title = QLabel("对话历史")
        title.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        layout.addWidget(title)
        
        layout.addStretch()
        
        # 清空按钮
        self.clear_btn = QPushButton("清空")
        self.clear_btn.setMaximumWidth(60)
        self.clear_btn.clicked.connect(self.clear_history)
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 10px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        layout.addWidget(self.clear_btn)
        
        header.setLayout(layout)
        return header
    
    def create_message_area(self, parent_layout):
        """创建消息显示区域"""
        # 滚动区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # 消息容器
        self.messages_widget = QWidget()
        self.messages_layout = QVBoxLayout()
        self.messages_layout.setContentsMargins(0, 0, 0, 0)
        self.messages_layout.setSpacing(5)
        
        # 添加欢迎消息
        self.add_welcome_message()
        
        # 添加弹性空间，使消息从底部开始
        self.messages_layout.addStretch()
        
        self.messages_widget.setLayout(self.messages_layout)
        self.scroll_area.setWidget(self.messages_widget)
        
        parent_layout.addWidget(self.scroll_area)
    
    def add_welcome_message(self):
        """添加欢迎消息"""
        welcome_text = ("您好！我是iPheno，来自AI4Bread团队的农业视觉问答助手。\n\n"
                       "请上传农业相关图片，您可以：\n"
                       "• 绘制感兴趣的区域\n"
                       "• 询问关于图片或特定区域的问题\n"
                       "• 获得专业的农业分析和建议\n\n"
                       "让我们开始吧！")
        
        container = MessageContainer(welcome_text, False)
        self.messages_layout.addWidget(container)
        self.messages.append({
            'text': welcome_text,
            'is_user': False,
            'timestamp': datetime.datetime.now(),
            'widget': container
        })
    
    def add_user_message(self, message):
        """添加用户消息"""
        timestamp = datetime.datetime.now()
        container = MessageContainer(message, True, timestamp)
        
        # 移除弹性空间
        if self.messages_layout.count() > 0:
            last_item = self.messages_layout.itemAt(self.messages_layout.count() - 1)
            if last_item.widget() is None:  # 弹性空间
                self.messages_layout.removeItem(last_item)
        
        self.messages_layout.addWidget(container)
        
        # 重新添加弹性空间
        self.messages_layout.addStretch()
        
        # 保存消息
        self.messages.append({
            'text': message,
            'is_user': True,
            'timestamp': timestamp,
            'widget': container
        })
        
        # 滚动到底部
        QTimer.singleShot(50, self.scroll_to_bottom)
    
    def add_assistant_message(self, message):
        """添加助手消息"""
        # 移除打字指示器
        self.remove_typing_indicator()
        
        timestamp = datetime.datetime.now()
        container = MessageContainer(message, False, timestamp)
        
        # 移除弹性空间
        if self.messages_layout.count() > 0:
            last_item = self.messages_layout.itemAt(self.messages_layout.count() - 1)
            if last_item.widget() is None:  # 弹性空间
                self.messages_layout.removeItem(last_item)
        
        self.messages_layout.addWidget(container)
        
        # 重新添加弹性空间
        self.messages_layout.addStretch()
        
        # 保存消息
        self.messages.append({
            'text': message,
            'is_user': False,
            'timestamp': timestamp,
            'widget': container
        })
        
        # 滚动到底部
        QTimer.singleShot(50, self.scroll_to_bottom)
    
    def show_typing_indicator(self):
        """显示打字指示器"""
        if self.typing_indicator is not None:
            return  # 已经在显示
        
        self.typing_indicator = TypingIndicator()
        
        # 移除弹性空间
        if self.messages_layout.count() > 0:
            last_item = self.messages_layout.itemAt(self.messages_layout.count() - 1)
            if last_item.widget() is None:  # 弹性空间
                self.messages_layout.removeItem(last_item)
        
        self.messages_layout.addWidget(self.typing_indicator)
        
        # 重新添加弹性空间
        self.messages_layout.addStretch()
        
        # 开始动画
        self.typing_indicator.start_animation()
        
        # 滚动到底部
        QTimer.singleShot(50, self.scroll_to_bottom)
    
    def remove_typing_indicator(self):
        """移除打字指示器"""
        if self.typing_indicator is not None:
            self.typing_indicator.stop_animation()
            self.messages_layout.removeWidget(self.typing_indicator)
            self.typing_indicator.deleteLater()
            self.typing_indicator = None
    
    def clear_history(self):
        """清空对话历史"""
        # 清空消息列表
        for message in self.messages:
            if message['widget']:
                self.messages_layout.removeWidget(message['widget'])
                message['widget'].deleteLater()
        
        self.messages.clear()
        
        # 移除打字指示器
        self.remove_typing_indicator()
        
        # 重新添加欢迎消息
        self.add_welcome_message()
    
    def scroll_to_bottom(self):
        """滚动到底部"""
        scrollbar = self.scroll_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def get_message_count(self):
        """获取消息数量"""
        return len(self.messages)
    
    def export_history(self):
        """导出对话历史"""
        history_text = []
        for message in self.messages:
            timestamp = message['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
            sender = "用户" if message['is_user'] else "助手"
            history_text.append(f"[{timestamp}] {sender}: {message['text']}")
        
        return "\n\n".join(history_text)