#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Config模块初始化文件
"""

from .settings import *

__all__ = [
    'APP_CONFIG', 'WINDOW_CONFIG', 'MODEL_CONFIG',
    'IMAGE_CONFIG', 'DRAWING_CONFIG', 'CHAT_CONFIG',
    'RESOURCE_PATHS', 'STYLE_CONFIG',
    'get_resource_path', 'get_avatar_path', 'get_icon_path'
]