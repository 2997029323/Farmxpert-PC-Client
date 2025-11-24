#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyQt应用程序样式定义
"""

from config.settings import STYLE_CONFIG


def get_main_style():
    """获取主窗口样式"""
    return f"""
    QMainWindow {{
        background-color: {STYLE_CONFIG['background_color']};
        color: {STYLE_CONFIG['text_color']};
    }}

    QWidget {{
        background-color: {STYLE_CONFIG['background_color']};
        color: {STYLE_CONFIG['text_color']};
        font-family: "Microsoft YaHei", "Arial", sans-serif;
    }}

    /* 标题样式 */
    QLabel#title_label {{
        font-size: 24px;
        font-weight: bold;
        color: {STYLE_CONFIG['text_color']};
        padding: 10px;
    }}

    /* 卡片容器样式 */
    QFrame.card {{
        background-color: {STYLE_CONFIG['card_background']};
        border: 1px solid {STYLE_CONFIG['border_color']};
        border-radius: 8px;
        padding: 15px;
        margin: 5px;
    }}

    /* 按钮样式 */
    QPushButton {{
        background-color: #f0f2f6;
        color: {STYLE_CONFIG['text_color']};
        border: 1px solid #cccccc;
        border-radius: 5px;
        padding: 8px 16px;
        font-size: 14px;
        min-height: 20px;
    }}

    QPushButton:hover {{
        background-color: #e0e2e6;
    }}

    QPushButton:pressed {{
        background-color: #d0d2d6;
    }}

    QPushButton:disabled {{
        background-color: #f5f5f5;
        color: #999999;
        border-color: #e0e0e0;
    }}

    /* 主要按钮样式 */
    QPushButton.primary {{
        background-color: {STYLE_CONFIG['primary_color']};
        color: white;
        border: none;
    }}

    QPushButton.primary:hover {{
        background-color: {STYLE_CONFIG['button_hover_color']};
    }}

    /* 文本输入框样式 */
    QTextEdit, QPlainTextEdit {{
        background-color: white;
        border: 1px solid {STYLE_CONFIG['border_color']};
        border-radius: 5px;
        padding: 8px;
        font-size: 14px;
        selection-background-color: {STYLE_CONFIG['secondary_color']};
    }}

    QTextEdit:focus, QPlainTextEdit:focus {{
        border-color: {STYLE_CONFIG['primary_color']};
    }}

    /* 标签样式 */
    QLabel {{
        color: {STYLE_CONFIG['text_color']};
        font-size: 14px;
    }}

    QLabel.section_title {{
        font-size: 16px;
        font-weight: bold;
        margin-bottom: 10px;
    }}

    QLabel.subsection_title {{
        font-size: 14px;
        font-weight: bold;
        margin-top: 10px;
        margin-bottom: 5px;
    }}

    /* 滚动条样式 */
    QScrollArea {{
        border: none;
        background-color: white;
    }}

    QScrollBar:vertical {{
        background-color: #f1f1f1;
        width: 12px;
        border-radius: 6px;
    }}

    QScrollBar::handle:vertical {{
        background-color: #c1c1c1;
        border-radius: 6px;
        min-height: 20px;
    }}

    QScrollBar::handle:vertical:hover {{
        background-color: #a8a8a8;
    }}

    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        border: none;
        background: none;
    }}

    /* 分割线样式 */
    QFrame[frameShape="4"] {{
        color: {STYLE_CONFIG['border_color']};
    }}

    /* 进度条样式 */
    QProgressBar {{
        border: 1px solid {STYLE_CONFIG['border_color']};
        border-radius: 5px;
        text-align: center;
        background-color: white;
    }}

    QProgressBar::chunk {{
        background-color: {STYLE_CONFIG['primary_color']};
        border-radius: 4px;
    }}

    /* 状态标签样式 */
    QLabel.status_info {{
        background-color: #e3f2fd;
        color: #0d47a1;
        border: 1px solid #bbdefb;
        border-radius: 4px;
        padding: 8px;
    }}

    QLabel.status_success {{
        background-color: #e8f5e9;
        color: #2e7d32;
        border: 1px solid #c8e6c9;
        border-radius: 4px;
        padding: 8px;
    }}

    QLabel.status_error {{
        background-color: #ffebee;
        color: #c62828;
        border: 1px solid #ffcdd2;
        border-radius: 4px;
        padding: 8px;
    }}

    QLabel.status_warning {{
        background-color: #fff3e0;
        color: #ef6c00;
        border: 1px solid #ffcc02;
        border-radius: 4px;
        padding: 8px;
    }}
    """


def get_chat_style():
    """获取聊天界面样式"""
    return f"""
    /* 聊天容器 */
    QScrollArea#chat_scroll {{
        background-color: white;
        border: 1px solid {STYLE_CONFIG['border_color']};
        border-radius: 5px;
    }}

    /* 聊天气泡 - 用户消息 */
    QFrame.user_message {{
        background-color: {CHAT_CONFIG['user_color']};
        border: 1px solid #b3e5fc;
        border-radius: 10px;
        padding: 10px;
        margin: 5px;
        max-width: 70%;
    }}

    /* 聊天气泡 - 模型回复 */
    QFrame.model_message {{
        background-color: {CHAT_CONFIG['model_color']};
        border: 1px solid #c8e6c9;
        border-radius: 10px;
        padding: 10px;
        margin: 5px;
        max-width: 70%;
    }}

    /* 头像样式 */
    QLabel.avatar {{
        border-radius: 20px;
        border: 2px solid {STYLE_CONFIG['border_color']};
        max-width: 40px;
        max-height: 40px;
        min-width: 40px;
        min-height: 40px;
    }}

    /* 消息文本样式 */
    QLabel.message_text {{
        font-size: 14px;
        line-height: 1.5;
        word-wrap: break-word;
    }}

    QLabel.message_sender {{
        font-weight: bold;
        font-size: 12px;
        color: #666666;
    }}

    QLabel.message_time {{
        font-size: 10px;
        color: #999999;
    }}
    """


def get_drawing_style():
    """获取绘制区域样式"""
    return f"""
    /* 绘制区域容器 */
    QLabel#drawing_canvas {{
        border: 2px solid {STYLE_CONFIG['border_color']};
        border-radius: 5px;
        background-color: white;
    }}

    /* 区域预览网格 */
    QFrame.region_preview {{
        border: 1px solid {STYLE_CONFIG['border_color']};
        border-radius: 5px;
        padding: 5px;
        margin: 2px;
        background-color: white;
    }}

    QLabel.region_preview_image {{
        border: 1px solid #ddd;
        border-radius: 3px;
    }}

    QPushButton.region_button {{
        font-size: 12px;
        padding: 4px 8px;
        margin-top: 5px;
    }}
    """


# 从配置导入聊天颜色
from config.settings import CHAT_CONFIG


def apply_styles(app):
    """应用所有样式到应用程序"""
    style = get_main_style() + get_chat_style() + get_drawing_style()
    app.setStyleSheet(style)