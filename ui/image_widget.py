#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图像处理组件
支持图像上传、显示、缩放等功能
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QFileDialog, QScrollArea, QFrame,
                           QButtonGroup, QRadioButton, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal, QMimeData
from PyQt5.QtGui import QPixmap, QDragEnterEvent, QDropEvent, QPainter, QPen, QColor, QImage
import os
from PIL import Image
import numpy as np

from core.utils import validate_image, resize_image, convert_image_format


class ImageDisplayLabel(QLabel):
    """自定义图像显示标签，支持拖拽上传"""
    
    image_dropped = pyqtSignal(str)  # 图像拖拽信号
    
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(400, 300)
        self.setFrameStyle(QFrame.Box)
        self.setStyleSheet("""
            QLabel {
                border: 2px dashed #cccccc;
                border-radius: 10px;
                background-color: #f9f9f9;
                color: #666666;
                font-size: 14px;
            }
            QLabel:hover {
                border-color: #4CAF50;
                background-color: #f0f8f0;
            }
        """)
        self.setText("拖拽图像到此处\n或点击选择文件")
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """拖拽进入事件"""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if len(urls) == 1 and urls[0].isLocalFile():
                file_path = urls[0].toLocalFile()
                if validate_image(file_path):
                    event.acceptProposedAction()
                    return
        event.ignore()
    
    def dropEvent(self, event: QDropEvent):
        """拖拽放下事件"""
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            self.image_dropped.emit(file_path)
            event.acceptProposedAction()
    
    def mousePressEvent(self, event):
        """鼠标点击事件"""
        if event.button() == Qt.LeftButton:
            self.image_dropped.emit("")  # 空字符串表示通过点击选择


class ImageWidget(QWidget):
    """图像处理组件"""
    
    image_loaded = pyqtSignal(object)  # 图像加载完成信号
    
    def __init__(self):
        super().__init__()
        self.current_image = None
        self.current_pixmap = None
        self.original_image = None
        self.scale_factor = 1.0
        self.init_ui()
    
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout()
        
        # 控制面板
        control_panel = self.create_control_panel()
        layout.addWidget(control_panel)
        
        # 图像显示区域
        self.create_image_display_area(layout)
        
        self.setLayout(layout)
    
    def create_control_panel(self):
        """创建控制面板"""
        panel = QFrame()
        panel.setFrameStyle(QFrame.StyledPanel)
        panel.setMaximumHeight(80)
        
        layout = QHBoxLayout()
        
        # 文件选择按钮
        self.open_btn = QPushButton("选择图像")
        self.open_btn.clicked.connect(self.open_image)
        layout.addWidget(self.open_btn)
        
        # 缩放控制
        layout.addWidget(QLabel("缩放:"))
        
        self.zoom_in_btn = QPushButton("放大")
        self.zoom_in_btn.clicked.connect(self.zoom_in)
        self.zoom_in_btn.setEnabled(False)
        layout.addWidget(self.zoom_in_btn)
        
        self.zoom_out_btn = QPushButton("缩小")
        self.zoom_out_btn.clicked.connect(self.zoom_out)
        self.zoom_out_btn.setEnabled(False)
        layout.addWidget(self.zoom_out_btn)
        
        self.fit_btn = QPushButton("适应窗口")
        self.fit_btn.clicked.connect(self.fit_to_window)
        self.fit_btn.setEnabled(False)
        layout.addWidget(self.fit_btn)
        
        self.reset_btn = QPushButton("原始大小")
        self.reset_btn.clicked.connect(self.reset_zoom)
        self.reset_btn.setEnabled(False)
        layout.addWidget(self.reset_btn)
        
        layout.addStretch()
        
        # 图像信息标签
        self.info_label = QLabel("未加载图像")
        layout.addWidget(self.info_label)
        
        panel.setLayout(layout)
        return panel
    
    def create_image_display_area(self, parent_layout):
        """创建图像显示区域"""
        # 滚动区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setAlignment(Qt.AlignCenter)
        
        # 图像标签
        self.image_label = ImageDisplayLabel()
        self.image_label.image_dropped.connect(self.handle_image_drop)
        
        self.scroll_area.setWidget(self.image_label)
        parent_layout.addWidget(self.scroll_area)
    
    def handle_image_drop(self, file_path):
        """处理图像拖拽或点击"""
        if file_path:
            self.load_image(file_path)
        else:
            self.open_image()
    
    def open_image(self):
        """打开图像文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择图像文件",
            "",
            "图像文件 (*.jpg *.jpeg *.png *.bmp *.tiff *.webp);;所有文件 (*)"
        )
        
        if file_path:
            self.load_image(file_path)
    
    def load_image(self, file_path):
        """加载图像"""
        try:
            # 验证图像文件
            if not validate_image(file_path):
                QMessageBox.warning(self, "错误", "无效的图像文件！")
                return
            
            # 使用PIL加载图像
            pil_image = Image.open(file_path)
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            # 保存原始图像
            self.original_image = pil_image.copy()
            self.current_image = pil_image
            
            # 转换为QPixmap
            self.update_pixmap()
            
            # 更新界面
            self.update_ui_after_load()
            
            # 发送信号
            self.image_loaded.emit(self.current_image)
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载图像失败：\n{str(e)}")
    
    def update_pixmap(self):
        """更新QPixmap显示"""
        if self.current_image is None:
            return
        
        # 将PIL图像转换为QPixmap
        img_array = np.array(self.current_image)
        height, width, channel = img_array.shape
        bytes_per_line = 3 * width
        
        # from PyQt5.QtGui import QImage
        q_image = QImage(img_array.data, width, height, bytes_per_line, QImage.Format_RGB888)
        self.current_pixmap = QPixmap.fromImage(q_image)
        
        # 应用缩放
        if self.scale_factor != 1.0:
            scaled_size = self.current_pixmap.size() * self.scale_factor
            self.current_pixmap = self.current_pixmap.scaled(
                scaled_size, 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
        
        # 显示图像
        self.image_label.setPixmap(self.current_pixmap)
        self.image_label.resize(self.current_pixmap.size())
    
    def update_ui_after_load(self):
        """加载图像后更新UI"""
        if self.current_image:
            width, height = self.current_image.size
            self.info_label.setText(f"图像大小: {width}×{height}")
            
            # 启用控制按钮
            self.zoom_in_btn.setEnabled(True)
            self.zoom_out_btn.setEnabled(True)
            self.fit_btn.setEnabled(True)
            self.reset_btn.setEnabled(True)
            
            # 重置缩放
            self.scale_factor = 1.0
            
            # 自动适应窗口
            self.fit_to_window()
    
    def zoom_in(self):
        """放大图像"""
        self.scale_factor *= 1.25
        self.update_pixmap()
    
    def zoom_out(self):
        """缩小图像"""
        self.scale_factor /= 1.25
        self.update_pixmap()
    
    def fit_to_window(self):
        """适应窗口大小"""
        if self.current_pixmap is None:
            return
        
        # 获取显示区域大小
        available_size = self.scroll_area.size()
        available_size.setWidth(available_size.width() - 20)  # 留出边距
        available_size.setHeight(available_size.height() - 20)
        
        # 计算缩放比例
        original_size = QPixmap.fromImage(
            QImage(np.array(self.current_image).data, 
                   self.current_image.size[0], 
                   self.current_image.size[1], 
                   3 * self.current_image.size[0], 
                   QImage.Format_RGB888)
        ).size()
        
        scale_x = available_size.width() / original_size.width()
        scale_y = available_size.height() / original_size.height()
        self.scale_factor = min(scale_x, scale_y, 1.0)  # 不超过原始大小
        
        self.update_pixmap()
    
    def reset_zoom(self):
        """重置为原始大小"""
        self.scale_factor = 1.0
        self.update_pixmap()
    
    def get_display_to_image_ratio(self):
        """获取显示坐标到图像坐标的比例"""
        if self.current_image is None or self.current_pixmap is None:
            return 1.0
        
        original_width = self.current_image.size[0]
        display_width = self.current_pixmap.width()
        
        return original_width / display_width if display_width > 0 else 1.0
    
    def display_to_image_coords(self, x, y):
        """将显示坐标转换为图像坐标"""
        ratio = self.get_display_to_image_ratio()
        return int(x * ratio), int(y * ratio)
    
    def image_to_display_coords(self, x, y):
        """将图像坐标转换为显示坐标"""
        ratio = self.get_display_to_image_ratio()
        return int(x / ratio), int(y / ratio)