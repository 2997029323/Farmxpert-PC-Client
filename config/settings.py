#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应用程序设置配置
"""

import os

# 应用信息
APP_NAME = "农业视觉问答助手"
APP_VERSION = "1.0.0"
APP_AUTHOR = "农业AI实验室"
APP_DESCRIPTION = "基于多模态大语言模型的农业视觉问答应用"

# 窗口设置
WINDOW_CONFIG = {
    "default_width": 1400,
    "default_height": 900,
    "minimum_width": 1200,
    "minimum_height": 800,
    "remember_size": True,
    "center_on_screen": True
}

# 图像处理设置
IMAGE_CONFIG = {
    "supported_formats": [".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"],
    "max_display_size": (1024, 1024),
    "thumbnail_size": (200, 200),
    "default_quality": 95,
    "enable_gpu_acceleration": False
}

# 区域绘制设置
DRAWING_CONFIG = {
    "region_color": "#228B22",  # 森林绿
    "current_color": "#FFA500",  # 橙色
    "point_radius": 4,
    "line_width": 2,
    "fill_alpha": 50,
    "max_regions": 20,
    "auto_simplify": True,
    "simplify_tolerance": 2.0
}

# 聊天界面设置
CHAT_CONFIG = {
    "max_history": 100,
    "auto_scroll": True,
    "show_timestamps": True,
    "enable_export": True,
    "bubble_style": "modern",
    "animation_duration": 300
}

# 模型推理设置
INFERENCE_CONFIG = {
    "show_progress": True,
    "enable_cancellation": True,
    "retry_attempts": 3,
    "retry_delay": 2,
    "cache_responses": False,
    "log_requests": True
}

# 文件路径设置
PATHS = {
    "resources": "resources",
    "icons": "resources/icons",
    "avatars": "resources/avatars",
    "config": "config",
    "logs": "logs",
    "cache": "cache",
    "exports": "exports"
}

# 日志设置
LOGGING_CONFIG = {
    "level": "INFO",
    "max_file_size": 10 * 1024 * 1024,  # 10MB
    "backup_count": 5,
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "console_output": True,
    "file_output": True
}

# 性能设置
PERFORMANCE_CONFIG = {
    "max_memory_usage": 2048,  # MB
    "thread_pool_size": 4,
    "enable_caching": True,
    "cache_size": 100,
    "gc_interval": 300  # seconds
}

# 用户界面设置
UI_CONFIG = {
    "theme": "light",  # light, dark, auto
    "font_family": "Microsoft YaHei",
    "font_size": 10,
    "enable_animations": True,
    "tooltip_delay": 500,
    "status_timeout": 5000
}

# 快捷键设置
SHORTCUTS = {
    "open_image": "Ctrl+O",
    "submit_question": "Ctrl+Return",
    "clear_regions": "Ctrl+Shift+C",
    "clear_chat": "Ctrl+Shift+H",
    "export_chat": "Ctrl+E",
    "quit": "Ctrl+Q",
    "zoom_in": "Ctrl+=",
    "zoom_out": "Ctrl+-",
    "fit_window": "Ctrl+0"
}

# 网络设置
NETWORK_CONFIG = {
    "connection_timeout": 30,
    "read_timeout": 60,
    "max_retries": 3,
    "proxy": {
        "enabled": False,
        "http": "",
        "https": "",
        "username": "",
        "password": ""
    }
}

# 安全设置
SECURITY_CONFIG = {
    "validate_uploads": True,
    "max_file_size": 50 * 1024 * 1024,  # 50MB
    "allowed_mime_types": [
        "image/jpeg",
        "image/png",
        "image/bmp",
        "image/tiff",
        "image/webp"
    ],
    "encrypt_cache": False,
    "clear_on_exit": False
}

# 实验性功能
EXPERIMENTAL_CONFIG = {
    "enable_batch_processing": False,
    "enable_region_templates": False,
    "enable_voice_input": False,
    "enable_auto_save": False,
    "enable_cloud_sync": False
}


def create_directories():
    """创建必要的目录"""
    for path in PATHS.values():
        os.makedirs(path, exist_ok=True)


def get_config_value(section, key, default=None):
    """获取配置值"""
    config_map = {
        "window": WINDOW_CONFIG,
        "image": IMAGE_CONFIG,
        "drawing": DRAWING_CONFIG,
        "chat": CHAT_CONFIG,
        "inference": INFERENCE_CONFIG,
        "logging": LOGGING_CONFIG,
        "performance": PERFORMANCE_CONFIG,
        "ui": UI_CONFIG,
        "shortcuts": SHORTCUTS,
        "network": NETWORK_CONFIG,
        "security": SECURITY_CONFIG,
        "experimental": EXPERIMENTAL_CONFIG
    }

    return config_map.get(section, {}).get(key, default)


def set_config_value(section, key, value):
    """设置配置值"""
    config_map = {
        "window": WINDOW_CONFIG,
        "image": IMAGE_CONFIG,
        "drawing": DRAWING_CONFIG,
        "chat": CHAT_CONFIG,
        "inference": INFERENCE_CONFIG,
        "logging": LOGGING_CONFIG,
        "performance": PERFORMANCE_CONFIG,
        "ui": UI_CONFIG,
        "shortcuts": SHORTCUTS,
        "network": NETWORK_CONFIG,
        "security": SECURITY_CONFIG,
        "experimental": EXPERIMENTAL_CONFIG
    }

    if section in config_map:
        config_map[section][key] = value
        return True
    return False