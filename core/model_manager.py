#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模型管理模块
负责AI模型的加载、推理和管理
"""

from PyQt5.QtCore import QObject, pyqtSignal, QThread, QTimer
import threading
import time
import base64
import io
import json
import requests
from PIL import Image
import numpy as np

from .utils import process_regions_for_model, encode_image_base64


class InferenceWorker(QThread):
    """推理工作线程"""
    
    finished = pyqtSignal(str)  # 推理完成信号
    error = pyqtSignal(str)     # 错误信号
    progress = pyqtSignal(int)  # 进度信号
    
    def __init__(self, model_manager, question, image, regions):
        super().__init__()
        self.model_manager = model_manager
        self.question = question
        self.image = image
        self.regions = regions
        self.is_cancelled = False
    
    def run(self):
        """运行推理"""
        try:
            # 模拟进度更新
            self.progress.emit(10)
            
            if self.is_cancelled:
                return
            
            # 预处理图像和区域
            processed_data = self.model_manager._preprocess_input(
                self.question, self.image, self.regions
            )
            
            self.progress.emit(30)
            
            if self.is_cancelled:
                return
            
            # 执行推理
            result = self.model_manager._run_inference(processed_data)
            
            self.progress.emit(80)
            
            if self.is_cancelled:
                return
            
            # 后处理结果
            answer = self.model_manager._postprocess_result(result)
            
            self.progress.emit(100)
            
            if not self.is_cancelled:
                self.finished.emit(answer)
                
        except Exception as e:
            if not self.is_cancelled:
                self.error.emit(str(e))
    
    def cancel(self):
        """取消推理"""
        self.is_cancelled = True


class ModelManager(QObject):
    """模型管理器"""
    
    # 信号定义
    model_loaded = pyqtSignal()           # 模型加载完成
    model_load_failed = pyqtSignal(str)   # 模型加载失败
    inference_started = pyqtSignal()      # 推理开始
    inference_finished = pyqtSignal(str)  # 推理完成
    inference_progress = pyqtSignal(int)  # 推理进度
    error_occurred = pyqtSignal(str)      # 错误发生
    
    def __init__(self):
        super().__init__()
        self.model = None
        self.is_loaded = False
        self.current_worker = None
        self.model_config = self.load_model_config()
        
        # 自动加载模型
        QTimer.singleShot(1000, self.load_model)

    def load_model_config(self):
        default_config = {
            "model_type": "api",
            "api_url": "https://xiaoai.plus/v1/chat/completions",
            "health_url": "https://xiaoai.plus/v1/models",
            "model_name": "gpt-4o",
            "api_key": "",  # 默认空
            "timeout": 60,
            "max_tokens": 2048,
            "temperature": 0.7
        }
        try:
            with open("config/model_config.json", "r", encoding="utf-8") as f:
                config = json.load(f)
                cfg = {**default_config, **config}
        except FileNotFoundError:
            cfg = default_config

        # 允许用环境变量兜底
        import os
        if not cfg["api_key"]:
            cfg["api_key"] = os.getenv("OPENAI_API_KEY", "")

        return cfg
    
    def load_model(self):
        """加载模型"""
        try:
            if self.model_config["model_type"] == "api":
                self._load_api_model()
            else:
                self._load_local_model()
                
        except Exception as e:
            self.model_load_failed.emit(f"模型加载失败: {str(e)}")

    def _load_api_model(self):
        """加载API模型（OpenAI 兼容）"""
        try:
            headers = {"Authorization": f"Bearer {self.model_config['api_key']}"}
            health_url = self.model_config.get("health_url") or self.model_config["api_url"].rsplit("/", 1)[
                0] + "/models"
            resp = requests.get(health_url, headers=headers, timeout=10)

            if resp.status_code == 200:
                # 可选：检查目标模型是否存在（有些代理不列出模型，此步可跳过）
                # data = resp.json().get("data", [])
                # models = {m.get("id") for m in data if isinstance(m, dict)}
                # if self.model_config["model_name"] not in models:
                #     print("提示：目标模型可能不在 models 列表中，但不影响调用。")
                self.is_loaded = True
                self.model_loaded.emit()
            else:
                raise Exception(f"探活失败: {resp.status_code} {resp.text[:200]}")

        except requests.exceptions.RequestException as e:
            raise Exception(f"无法连接到 OpenAI 兼容 API: {str(e)}")
    
    def _load_local_model(self):
        """加载本地模型"""
        # 这里可以添加本地模型加载逻辑
        # 例如使用transformers库加载本地模型
        raise NotImplementedError("本地模型加载功能待实现")
    
    def process_question(self, question, image, regions):
        """处理问题"""
        if not self.is_loaded:
            self.error_occurred.emit("模型未加载")
            return
        
        # 取消当前推理
        if self.current_worker and self.current_worker.isRunning():
            self.current_worker.cancel()
            self.current_worker.wait()
        
        # 创建新的推理线程
        self.current_worker = InferenceWorker(self, question, image, regions)
        self.current_worker.finished.connect(self._on_inference_finished)
        self.current_worker.error.connect(self._on_inference_error)
        self.current_worker.progress.connect(self.inference_progress.emit)
        
        # 发送开始信号
        self.inference_started.emit()
        
        # 开始推理
        self.current_worker.start()

    def _preprocess_input(self, question, image, regions):
        from PIL import ImageDraw

        image_base64 = encode_image_base64(image)
        region_info = process_regions_for_model(regions, image.size)

        # 生成每个 region 的裁剪图（最小外接矩形；如需更精确可以做多边形掩膜）
        region_crops = []
        for idx, r in enumerate(region_info, 1):
            xs = [p[0] for p in r["points"]]
            ys = [p[1] for p in r["points"]]
            x1, y1, x2, y2 = max(int(min(xs)), 0), max(int(min(ys)), 0), int(max(xs)), int(max(ys))
            crop = image.crop((x1, y1, x2, y2))
            # 可选：在裁剪图上把多边形描出来，增强可读性
            # draw = ImageDraw.Draw(crop); ...（略）
            buf_b64 = encode_image_base64(crop)
            region_crops.append({"tag": f"region{idx}", "bbox": (x1, y1, x2, y2), "b64": buf_b64})

        prompt = self._build_prompt(question, region_info)

        return {
            "prompt": prompt,
            "image": image_base64,  # 整图
            "regions": region_info,  # 文本信息
            "region_crops": region_crops,  # 新增：裁剪图
            "original_question": question
        }
    
    def _build_prompt(self, question, region_info):
        """构建提示词"""
        base_prompt = """你是一个专业的农业视觉分析助手。请根据提供的图像回答用户的问题。

                    图像信息：
                    - 这是一张农业相关的图片
                    - 用户可能在图片上标注了感兴趣的区域
                    
                    """
        
        if region_info:
            base_prompt += "用户标注的区域信息：\n"
            for i, region in enumerate(region_info, 1):
                base_prompt += f"区域{i}: 包含{len(region['points'])}个坐标点\n"
            base_prompt += "\n"
        
        base_prompt += f"用户问题：{question}\n\n"
        base_prompt += """请提供专业、详细的回答。如果问题涉及特定区域，请结合区域信息进行分析。
                        回答要求：
                        1. 使用中文回答
                        2. 内容要专业、准确
                        3. 如果涉及农业诊断，请提供具体建议
                        4. 保持回答的结构化和易读性"""
        
        return base_prompt
    
    def _run_inference(self, processed_data):
        """运行推理"""
        if self.model_config["model_type"] == "api":
            return self._run_api_inference(processed_data)
        else:
            return self._run_local_inference(processed_data)

    def _convert_regions_to_polygons(self,original_data_list):
        """
        将包含区域信息（包括点的元组列表）的数据结构转换为
        指定的多边形坐标点列表格式。

        Args:
            original_data_list (list): 原始数据列表，其中每个字典代表一个区域，
                                       包含 'points' 键，其值为 (x, y) 元组列表。

        Returns:
            dict: 包含一个 'polygons' 键的字典。'polygons' 的值是一个列表，
                  其中每个元素代表一个区域的多边形，它又是一个字典列表，
                  每个字典包含 'x' 和 'y' 键（浮点数）。
                  示例: {"polygons": [[{'x': x1, 'y': y1}, ...], [{'x': x2, 'y': y2}, ...]]}
        """
        converted_polygons_list = []

        for region in original_data_list:
            if 'points' in region and isinstance(region['points'], list):
                points_tuples = region['points']
                # 将 (x, y) 元组转换为 {'x': x, 'y': y} 字典的列表
                # 将整数坐标转换为浮点数，以符合目标格式
                converted_points = [{'x': float(x), 'y': float(y)} for x, y in points_tuples]
                converted_polygons_list.append(converted_points)
            else:
                # 如果某个区域没有 'points' 键或其格式不正确，可以选择跳过或报错
                print(
                    f"Warning: Region ID {region.get('id', 'N/A')} is missing 'points' key or it's not a list. Skipping.")

        output_data = {"polygons": converted_polygons_list}
        return output_data
    def _run_api_inference(self, processed_data):
        try:
            ###调用iPheno的api
            # 规范

            # payload = {
            #     "image_base64": image_b64,
            #     "polygons": st.session_state.polygons,
            #     "prompt": prompt,
            #     "chat_history_messages": serializable_history
            # }


            BACKEND_API_URL = "https://farmxpert.vip.cpolar.cn"
            payload_iPheno = {
                "image_base64": processed_data['image'],
                "polygons": self._convert_regions_to_polygons(processed_data['regions'])["polygons"],
                "prompt": processed_data['original_question'],
                "chat_history_messages": []
            }
            response_from_api = requests.post(
                f"{BACKEND_API_URL}/infer",
                json=payload_iPheno,
                timeout=300
            )
            response_from_api.raise_for_status()
            api_data = response_from_api.json()

            if api_data.get("status") == "success":
                response = api_data.get("response", "No response from model.")
            else:
                response = f"API error: {api_data.get('message', 'Unknown error')}"
            result = {
                "choices": [
                    {
                        "message": {
                            "content": response
                        }
                    }
                ]
            }
            return result
        ####
        except Exception as e:
            try:
                content = []
                # 先放说明文本 + 整图
                content.append({"type": "text", "text": processed_data["prompt"]})
                content.append({"type": "image_url",
                                "image_url": {"url": f"data:image/png;base64,{processed_data['image']}"}})

                # 再逐个放区域的文本提示 + 裁剪图
                for rc in processed_data.get("region_crops", []):
                    content.append({"type": "text",
                                    "text": f"下面这张图是 <{rc['tag']}> 的区域裁剪（bbox={rc['bbox']}）。"})
                    content.append({"type": "image_url",
                                    "image_url": {"url": f"data:image/png;base64,{rc['b64']}"}})

                payload = {
                    "model": self.model_config["model_name"],
                    "messages": [{"role": "user", "content": content}],
                    "temperature": self.model_config["temperature"],
                    "max_tokens": self.model_config["max_tokens"]
                }
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.model_config['api_key']}"
                }
                resp = requests.post(self.model_config["api_url"], json=payload,
                                     headers=headers, timeout=self.model_config["timeout"])

                if resp.status_code == 200:
                    return resp.json()
                raise Exception(f"API请求失败，状态码: {resp.status_code}，响应: {resp.text[:500]}")
            except requests.exceptions.Timeout:
                raise Exception("API请求超时")
            except requests.exceptions.RequestException as e:
                raise Exception(f"API请求错误: {str(e)}")
    
    def _run_local_inference(self, processed_data):
        """运行本地推理"""
        # 本地模型推理逻辑待实现
        raise NotImplementedError("本地模型推理功能待实现")

    def _postprocess_result(self, result):
        """后处理结果（OpenAI 兼容）"""
        try:
            if self.model_config["model_type"] == "api":
                choices = result.get("choices", [])
                if choices and "message" in choices[0]:
                    answer = choices[0]["message"].get("content", "") or ""
                else:
                    answer = "抱歉，无法生成回答。"
            else:
                answer = str(result)

            answer = answer.strip()
            if not answer:
                answer = "抱歉，无法生成回答。请重新尝试。"

            return answer

        except Exception as e:
            return f"处理回答时出错: {str(e)}"
    
    def _on_inference_finished(self, answer):
        """推理完成处理"""
        self.inference_finished.emit(answer)
        self.current_worker = None
    
    def _on_inference_error(self, error_msg):
        """推理错误处理"""
        self.error_occurred.emit(error_msg)
        self.current_worker = None
    
    def cancel_inference(self):
        """取消当前推理"""
        if self.current_worker and self.current_worker.isRunning():
            self.current_worker.cancel()
            self.current_worker.wait()
            self.current_worker = None
    
    def is_model_loaded(self):
        """检查模型是否已加载"""
        return self.is_loaded
    
    def get_model_info(self):
        """获取模型信息"""
        return {
            "type": self.model_config["model_type"],
            "name": self.model_config.get("model_name", "Unknown"),
            "status": "已加载" if self.is_loaded else "未加载"
        }
    
    def cleanup(self):
        """清理资源"""
        self.cancel_inference()
        self.model = None
        self.is_loaded = False


# 模拟推理函数（当没有实际模型时使用）
def simulate_inference(question, image, regions):
    """模拟推理过程"""
    import random
    
    # 模拟处理时间
    time.sleep(random.uniform(1, 3))
    
    # 生成模拟回答
    answers = [
        f"根据图像分析，我观察到以下内容：\n\n针对您的问题：'{question}'\n\n这是一张农业相关的图片。图像中显示了植物或农作物的情况。",
        
        f"基于您提供的图像和问题：'{question}'\n\n我可以看到图片中包含了农业场景。如果您标注了特定区域，我建议重点关注这些区域的植物健康状况。",
        
        f"关于您的问题：'{question}'\n\n从图像分析来看，这里有几个关键观察点：\n1. 植物的整体生长状况\n2. 可能的病虫害迹象\n3. 土壤和环境条件\n\n建议进行进一步的实地检查以确认诊断。"
    ]
    
    return random.choice(answers)