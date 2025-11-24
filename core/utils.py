#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具函数模块
包含图像处理、多边形处理等实用函数
"""

import os
import base64
import io
import json
from typing import List, Tuple, Dict, Any, Optional
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import cv2


def validate_image(file_path: str) -> bool:
    """
    验证图像文件是否有效
    
    Args:
        file_path: 图像文件路径
        
    Returns:
        bool: 图像是否有效
    """
    try:
        if not os.path.exists(file_path):
            return False
        
        # 检查文件扩展名
        valid_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in valid_extensions:
            return False
        
        # 尝试打开图像
        with Image.open(file_path) as img:
            img.verify()  # 验证图像完整性
        
        return True
        
    except Exception:
        return False


def resize_image(image: Image.Image, max_size: Tuple[int, int] = (1024, 1024)) -> Image.Image:
    """
    调整图像大小，保持宽高比
    
    Args:
        image: PIL图像对象
        max_size: 最大尺寸 (width, height)
        
    Returns:
        调整后的图像
    """
    original_size = image.size
    
    # 计算缩放比例
    scale = min(max_size[0] / original_size[0], max_size[1] / original_size[1])
    
    if scale < 1:
        new_size = (int(original_size[0] * scale), int(original_size[1] * scale))
        return image.resize(new_size, Image.Resampling.LANCZOS)
    
    return image


def convert_image_format(image: Image.Image, target_format: str = 'RGB') -> Image.Image:
    """
    转换图像格式
    
    Args:
        image: PIL图像对象
        target_format: 目标格式
        
    Returns:
        转换后的图像
    """
    if image.mode != target_format:
        return image.convert(target_format)
    return image


def encode_image_base64(image: Image.Image, format: str = 'JPEG', quality: int = 95) -> str:
    """
    将PIL图像编码为base64字符串
    
    Args:
        image: PIL图像对象
        format: 图像格式
        quality: 图像质量 (1-100)
        
    Returns:
        base64编码的图像字符串
    """
    buffer = io.BytesIO()
    
    # 确保图像格式正确
    if format.upper() == 'JPEG' and image.mode != 'RGB':
        image = image.convert('RGB')
    
    image.save(buffer, format=format, quality=quality)
    buffer.seek(0)
    
    encoded_image = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return encoded_image


def create_polygon_mask(points: List[Tuple[float, float]], image_size: Tuple[int, int]) -> np.ndarray:
    """
    根据多边形点创建遮罩
    
    Args:
        points: 多边形顶点坐标列表
        image_size: 图像尺寸 (width, height)
        
    Returns:
        二值遮罩数组
    """
    mask = Image.new('L', image_size, 0)
    
    if len(points) >= 3:
        # 转换坐标为整数
        int_points = [(int(x), int(y)) for x, y in points]
        
        # 绘制多边形
        ImageDraw.Draw(mask).polygon(int_points, outline=255, fill=255)
    
    return np.array(mask)


def calculate_polygon_area(points: List[Tuple[float, float]]) -> float:
    """
    计算多边形面积（使用鞋带公式）
    
    Args:
        points: 多边形顶点坐标列表
        
    Returns:
        多边形面积
    """
    if len(points) < 3:
        return 0.0
    
    area = 0.0
    n = len(points)
    
    for i in range(n):
        j = (i + 1) % n
        area += points[i][0] * points[j][1]
        area -= points[j][0] * points[i][1]
    
    return abs(area) / 2.0


def point_in_polygon(point: Tuple[float, float], polygon: List[Tuple[float, float]]) -> bool:
    """
    判断点是否在多边形内（射线法）
    
    Args:
        point: 测试点坐标
        polygon: 多边形顶点坐标列表
        
    Returns:
        点是否在多边形内
    """
    x, y = point
    n = len(polygon)
    inside = False
    
    p1x, p1y = polygon[0]
    for i in range(1, n + 1):
        p2x, p2y = polygon[i % n]
        
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        
        p1x, p1y = p2x, p2y
    
    return inside


def simplify_polygon(points: List[Tuple[float, float]], tolerance: float = 2.0) -> List[Tuple[float, float]]:
    """
    简化多边形（道格拉斯-普克算法）
    
    Args:
        points: 原始多边形顶点
        tolerance: 简化容差
        
    Returns:
        简化后的顶点列表
    """
    if len(points) <= 2:
        return points
    
    def perpendicular_distance(point, line_start, line_end):
        """计算点到直线的垂直距离"""
        if line_start == line_end:
            return ((point[0] - line_start[0]) ** 2 + (point[1] - line_start[1]) ** 2) ** 0.5
        
        A = line_end[1] - line_start[1]
        B = line_start[0] - line_end[0]
        C = line_end[0] * line_start[1] - line_start[0] * line_end[1]
        
        return abs(A * point[0] + B * point[1] + C) / (A ** 2 + B ** 2) ** 0.5
    
    def douglas_peucker(points_list, epsilon):
        """递归简化"""
        if len(points_list) <= 2:
            return points_list
        
        # 找到距离最大的点
        max_distance = 0
        index = 0
        end = len(points_list) - 1
        
        for i in range(1, end):
            distance = perpendicular_distance(points_list[i], points_list[0], points_list[end])
            if distance > max_distance:
                index = i
                max_distance = distance
        
        # 如果最大距离大于阈值，递归简化
        if max_distance > epsilon:
            left = douglas_peucker(points_list[:index + 1], epsilon)
            right = douglas_peucker(points_list[index:], epsilon)
            
            return left[:-1] + right
        else:
            return [points_list[0], points_list[end]]
    
    return douglas_peucker(points, tolerance)


def process_regions_for_model(regions: List[Dict], image_size: Tuple[int, int]) -> List[Dict]:
    """
    为模型处理区域信息
    
    Args:
        regions: 区域信息列表
        image_size: 图像尺寸
        
    Returns:
        处理后的区域信息
    """
    processed_regions = []
    
    for region in regions:
        if 'points' not in region or len(region['points']) < 3:
            continue
        
        points = region['points']
        
        # 计算区域属性
        area = calculate_polygon_area(points)
        
        # 计算边界框
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        bbox = {
            'x_min': min(xs),
            'y_min': min(ys),
            'x_max': max(xs),
            'y_max': max(ys)
        }
        
        # 计算中心点
        center = {
            'x': sum(xs) / len(xs),
            'y': sum(ys) / len(ys)
        }
        
        # 相对位置（相对于图像大小）
        relative_center = {
            'x': center['x'] / image_size[0],
            'y': center['y'] / image_size[1]
        }
        
        relative_area = area / (image_size[0] * image_size[1])
        
        processed_region = {
            'id': region.get('id', 0),
            'name': region.get('name', ''),
            'points': points,
            'area': area,
            'relative_area': relative_area,
            'bbox': bbox,
            'center': center,
            'relative_center': relative_center,
            'point_count': len(points)
        }
        
        processed_regions.append(processed_region)
    
    return processed_regions


def extract_image_features(image: Image.Image) -> Dict[str, Any]:
    """
    提取图像特征信息
    
    Args:
        image: PIL图像对象
        
    Returns:
        图像特征字典
    """
    # 转换为numpy数组
    img_array = np.array(image)
    
    features = {
        'size': image.size,
        'mode': image.mode,
        'format': getattr(image, 'format', None),
        'has_transparency': image.mode in ('RGBA', 'LA') or 'transparency' in image.info
    }
    
    if len(img_array.shape) == 3:  # 彩色图像
        # 计算颜色统计
        features.update({
            'mean_rgb': np.mean(img_array, axis=(0, 1)).tolist(),
            'std_rgb': np.std(img_array, axis=(0, 1)).tolist(),
            'brightness': np.mean(img_array),
            'contrast': np.std(img_array)
        })
    else:  # 灰度图像
        features.update({
            'brightness': np.mean(img_array),
            'contrast': np.std(img_array)
        })
    
    return features


def save_config(config: Dict[str, Any], file_path: str) -> bool:
    """
    保存配置文件
    
    Args:
        config: 配置字典
        file_path: 保存路径
        
    Returns:
        是否保存成功
    """
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        return True
        
    except Exception as e:
        print(f"保存配置文件失败: {e}")
        return False


def load_config(file_path: str, default_config: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    加载配置文件
    
    Args:
        file_path: 配置文件路径
        default_config: 默认配置
        
    Returns:
        配置字典
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 如果有默认配置，合并配置
        if default_config:
            merged_config = default_config.copy()
            merged_config.update(config)
            return merged_config
        
        return config
        
    except FileNotFoundError:
        return default_config or {}
    except Exception as e:
        print(f"加载配置文件失败: {e}")
        return default_config or {}


def create_thumbnail(image: Image.Image, size: Tuple[int, int] = (200, 200)) -> Image.Image:
    """
    创建缩略图
    
    Args:
        image: 原始图像
        size: 缩略图尺寸
        
    Returns:
        缩略图
    """
    thumbnail = image.copy()
    thumbnail.thumbnail(size, Image.Resampling.LANCZOS)
    return thumbnail


def blend_images(base_image: Image.Image, overlay_image: Image.Image, alpha: float = 0.5) -> Image.Image:
    """
    混合两张图像
    
    Args:
        base_image: 基础图像
        overlay_image: 覆盖图像
        alpha: 混合透明度
        
    Returns:
        混合后的图像
    """
    if base_image.size != overlay_image.size:
        overlay_image = overlay_image.resize(base_image.size, Image.Resampling.LANCZOS)
    
    if base_image.mode != overlay_image.mode:
        overlay_image = overlay_image.convert(base_image.mode)
    
    return Image.blend(base_image, overlay_image, alpha)


def apply_image_filter(image: Image.Image, filter_type: str) -> Image.Image:
    """
    应用图像滤镜
    
    Args:
        image: 输入图像
        filter_type: 滤镜类型
        
    Returns:
        处理后的图像
    """
    filters = {
        'blur': ImageFilter.BLUR,
        'sharpen': ImageFilter.SHARPEN,
        'smooth': ImageFilter.SMOOTH,
        'detail': ImageFilter.DETAIL,
        'edge_enhance': ImageFilter.EDGE_ENHANCE,
        'find_edges': ImageFilter.FIND_EDGES
    }
    
    if filter_type in filters:
        return image.filter(filters[filter_type])
    
    return image


def log_error(error_msg: str, error_type: str = "ERROR") -> None:
    """
    记录错误日志
    
    Args:
        error_msg: 错误消息
        error_type: 错误类型
    """
    import datetime
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] {error_type}: {error_msg}"
    
    # 输出到控制台
    print(log_msg)
    
    # 可以添加文件日志记录
    try:
        os.makedirs("logs", exist_ok=True)
        with open("logs/error.log", "a", encoding="utf-8") as f:
            f.write(log_msg + "\n")
    except Exception:
        pass  # 忽略日志写入错误