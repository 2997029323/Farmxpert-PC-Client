#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
区域绘制组件（回退版，无缩放手势/滚轮缩放）
支持在图像上绘制多边形区域
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QFrame, QScrollArea, QMessageBox, QCheckBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QPoint
from PyQt5.QtGui import (
    QPainter, QPen, QColor, QBrush, QPolygon, QCursor, QFont, QPixmap
)
import numpy as np
from PIL import Image
from core.utils import create_polygon_mask


class DrawingArea(QLabel):
    """绘制区域组件（不支持缩放，仅滚动查看大图）"""

    region_added = pyqtSignal(list)  # 新区域添加信号

    def __init__(self):
        super().__init__()
        self.image = None              # PIL.Image
        self.base_pixmap = None        # 原始图像 QPixmap（不含标注）
        self.pixmap = None             # 叠加标注后的 QPixmap（原始大小）

        self.regions = []
        self.current_polygon = []
        self.is_drawing = False

        # 左上对齐，方便与 QScrollArea 搭配，坐标换算更简单
        self.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.setMouseTracking(True)
        self.setCursor(QCursor(Qt.CrossCursor))
        self.setFrameStyle(QFrame.Box)

        # 绘制样式：更醒目
        self.region_color = QColor(0, 180, 255)   # 已完成区域：青色
        self.current_color = QColor(255, 140, 0)  # 当前区域：深橙
        self.point_radius = 5
        self.line_width = 3

        self.setStyleSheet("""
            QLabel {
                border: 1px solid #cccccc;
                background-color: #202020;
            }
        """)

    def set_image(self, pil_image: Image.Image):
        """设置要绘制的图像"""
        self.image = pil_image
        self.update_display()
        self.clear_current_polygon()

    def update_display(self):
        if self.image is None:
            self.setText("请先加载图像")
        else:
            # PIL -> QPixmap（原始尺寸）
            img_array = np.array(self.image)
            h, w, _ = img_array.shape
            from PyQt5.QtGui import QImage
            qimg = QImage(img_array.data, w, h, 3 * w, QImage.Format_RGB888)
            self.base_pixmap = QPixmap.fromImage(qimg)

            # 在副本上画区域（原始尺寸）
            self.pixmap = self.base_pixmap.copy()
            self._draw_regions_on_pixmap()

            # 不做缩放：label 固定为图像大小，ScrollArea 负责滚动
            self.setPixmap(self.pixmap)
            self.setFixedSize(self.pixmap.size())

    def _draw_regions_on_pixmap(self):
        """在QPixmap上绘制所有区域"""
        if self.pixmap is None:
            return
        painter = QPainter(self.pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # 已完成区域（填充更实一些）
        for i, region in enumerate(self.regions):
            if len(region) >= 3:
                self._draw_polygon(painter, region, self.region_color, i + 1)

        # 正在绘制的边与点
        if len(self.current_polygon) >= 2:
            self._draw_polygon(painter, self.current_polygon, self.current_color)
        for pt in self.current_polygon:
            self._draw_point(painter, pt, self.current_color)

        painter.end()

    def _draw_polygon(self, painter, points, color, region_number=None):
        if len(points) < 2:
            return
        pen = QPen(color, self.line_width)
        painter.setPen(pen)

        if len(points) >= 3 and region_number is not None:
            fill = QColor(color)
            fill.setAlpha(110)  # 更不透明
            painter.setBrush(QBrush(fill))
            polygon = QPolygon([QPoint(int(p[0]), int(p[1])) for p in points])
            painter.drawPolygon(polygon)
            self._draw_region_number(painter, points, region_number)
        else:
            painter.setBrush(Qt.NoBrush)

        # 边线
        for i in range(len(points) - 1):
            p1 = QPoint(int(points[i][0]), int(points[i][1]))
            p2 = QPoint(int(points[i + 1][0]), int(points[i + 1][1]))
            painter.drawLine(p1, p2)
        if len(points) >= 3 and region_number is not None:
            painter.drawLine(QPoint(int(points[-1][0]), int(points[-1][1])),
                             QPoint(int(points[0][0]), int(points[0][1])))

    def _draw_point(self, painter, point, color):
        painter.setPen(QPen(color, 1))
        painter.setBrush(QBrush(color))
        c = QPoint(int(point[0]), int(point[1]))
        painter.drawEllipse(c, self.point_radius, self.point_radius)

    def _draw_region_number(self, painter, points, number):
        if len(points) < 3:
            return
        cx = sum(p[0] for p in points) / len(points)
        cy = sum(p[1] for p in points) / len(points)
        painter.setFont(QFont("Arial", 12, QFont.Bold))
        bg = QColor(self.region_color); bg.setAlpha(220)
        painter.setBrush(QBrush(bg)); painter.setPen(QPen(bg))
        r = 15
        painter.drawEllipse(QPoint(int(cx), int(cy)), r, r)
        painter.setPen(QPen(QColor(255, 255, 255)))
        painter.drawText(int(cx - 10), int(cy - 10), 20, 20, Qt.AlignCenter, str(number))

    # ---- 坐标换算（无缩放，左上对齐）----
    def get_image_coordinates(self, widget_pos):
        """将 QLabel 坐标转换为原图像素坐标"""
        if self.pixmap is None or self.image is None:
            return None
        x = widget_pos.x()
        y = widget_pos.y()
        w, h = self.image.size
        if 0 <= x < w and 0 <= y < h:
            return (x, y)
        return None

    # ---- 交互：绘制多边形 ----
    def mousePressEvent(self, event):
        if self.image is None:
            return
        if event.button() == Qt.LeftButton:
            img_pt = self.get_image_coordinates(event.pos())
            if img_pt is not None:
                self.add_point_to_current_polygon(img_pt)
        elif event.button() == Qt.RightButton:
            self.finish_current_polygon()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.finish_current_polygon()

    def add_point_to_current_polygon(self, point):
        self.current_polygon.append(point)
        self.is_drawing = True
        self.update_display()

    def finish_current_polygon(self):
        if len(self.current_polygon) >= 3:
            self.regions.append(self.current_polygon.copy())
            self.region_added.emit(self.current_polygon.copy())
            self.clear_current_polygon()
            self.update_display()

    def clear_current_polygon(self):
        self.current_polygon = []
        self.is_drawing = False

    def clear_all_regions(self):
        self.regions = []
        self.clear_current_polygon()
        self.update_display()

    def remove_region(self, index):
        if 0 <= index < len(self.regions):
            self.regions.pop(index)
            self.update_display()

    def get_regions(self):
        return self.regions.copy()


class RegionDrawingWidget(QWidget):
    """区域绘制组件"""

    regions_changed = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.regions = []
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout()

        # 左侧：绘制区域
        left_panel = self.create_drawing_panel()
        layout.addWidget(left_panel, 3)

        # 右侧：区域列表
        right_panel = self.create_region_list_panel()
        layout.addWidget(right_panel, 1)

        self.setLayout(layout)

    def create_drawing_panel(self):
        panel = QFrame()
        panel.setFrameStyle(QFrame.StyledPanel)

        layout = QVBoxLayout()

        instruction = QLabel("左键点击绘制多边形，右键或双击完成绘制")
        instruction.setStyleSheet("color: #ccc; font-size: 12px; padding: 5px;")
        layout.addWidget(instruction)

        # 绘制区域 + ScrollArea（仅用于大图滚动）
        self.drawing_area = DrawingArea()
        self.drawing_area.region_added.connect(self.on_region_added)

        scroll = QScrollArea()
        scroll.setWidget(self.drawing_area)
        scroll.setWidgetResizable(False)  # 由图像大小决定滚动范围
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        scroll.setStyleSheet("QScrollArea { background: #202020; }")

        layout.addWidget(scroll)
        panel.setLayout(layout)
        return panel

    def create_region_list_panel(self):
        panel = QFrame()
        panel.setFrameStyle(QFrame.StyledPanel)

        layout = QVBoxLayout()

        # 标题
        title = QLabel("区域列表")
        title.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px;")
        layout.addWidget(title)

        # 区域列表
        self.region_list = QListWidget()
        self.region_list.itemDoubleClicked.connect(self.on_region_double_clicked)
        # 让深色主题更清晰（可选）
        self.region_list.setStyleSheet("""
            QListWidget {
                background: #1e1e1e; color: #ffffff; border: 1px solid #444;
            }
            QListWidget::item:selected {
                background: #2e7d32; color: #ffffff;
            }
        """)
        layout.addWidget(self.region_list)

        # 控制按钮
        button_layout = QVBoxLayout()

        self.delete_btn = QPushButton("删除选中")
        self.delete_btn.clicked.connect(self.delete_selected_region)
        self.delete_btn.setEnabled(False)
        button_layout.addWidget(self.delete_btn)

        self.clear_btn = QPushButton("清空所有")
        self.clear_btn.clicked.connect(self.clear_all_regions)
        button_layout.addWidget(self.clear_btn)

        layout.addLayout(button_layout)
        panel.setLayout(layout)
        return panel

    def set_image(self, pil_image):
        self.drawing_area.set_image(pil_image)
        self.clear_all_regions()

    def on_region_added(self, region_points):
        region_id = len(self.regions) + 1
        self.regions.append({'id': region_id, 'points': region_points, 'name': f"区域 {region_id}"})
        self.update_region_list()
        self.regions_changed.emit(self.regions)

    def update_region_list(self):
        self.region_list.clear()
        for region in self.regions:
            txt = f"{region['name']} ({len(region['points'])}个点)"
            item = QListWidgetItem(txt)
            item.setData(Qt.UserRole, region['id'])
            self.region_list.addItem(item)
        self.delete_btn.setEnabled(len(self.regions) > 0)

    def on_region_double_clicked(self, item):
        # 预留：编辑/定位功能
        pass

    def delete_selected_region(self):
        row = self.region_list.currentRow()
        if row >= 0:
            self.drawing_area.remove_region(row)
            self.regions.pop(row)
            # 重新编号
            for i, r in enumerate(self.regions):
                r['id'] = i + 1
                r['name'] = f"区域 {i + 1}"
            self.update_region_list()
            self.regions_changed.emit(self.regions)

    def clear_all_regions(self):
        self.regions = []
        self.drawing_area.clear_all_regions()
        self.update_region_list()
        self.regions_changed.emit(self.regions)

    def get_regions(self):
        return self.regions.copy()

    def get_region_masks(self, image_size):
        masks = []
        for r in self.regions:
            mask = create_polygon_mask(r['points'], image_size)
            masks.append({'id': r['id'], 'name': r['name'], 'mask': mask, 'points': r['points']})
        return masks