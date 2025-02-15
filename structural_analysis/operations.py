"""基础操作功能模块，提供MIDAS Civil的基本操作功能，包括：
- 打开软件
- 打开文件
- 运行分析
- 保存文件
"""

import subprocess
import time
import os
from .api import midas_api

class MidasOperations:
    @staticmethod
    def open_civil(civil_path):
        """
        打开MIDAS Civil NX软件
        
        参数:
        - civil_path: str, MIDAS Civil NX程序的完整路径
        
        返回:
        - None, 仅打印确认信息
        
        示例:
        >>> MidasOperations.open_civil("C:/Program Files/MIDAS/Civil/Civil.exe")
        """
        subprocess.Popen(civil_path)
        print("MIDAS CIVIL NX已开启")
        
    @staticmethod
    def open_file(civil_path, file_path):
        """
        打开指定的MIDAS模型文件
        
        参数:
        - civil_path: str, MIDAS Civil NX程序的完整路径
        - file_path: str, 要打开的模型文件(.mcb)的完整路径
        
        返回:
        - dict: API响应结果
        
        异常:
        - FileNotFoundError: 当指定的文件不存在时抛出
        
        注意:
        - 会等待30秒确保程序完全启动
        - 文件路径需要使用完整路径
        
        示例:
        >>> MidasOperations.open_file(
        ...     "C:/Program Files/MIDAS/Civil/Civil.exe",
        ...     "C:/Projects/bridge.mcb"
        ... )
        """
        # 启动MIDAS Civil
        MidasOperations.open_civil(civil_path)
        
        # 等待程序启动完成
        time.sleep(30)
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
            
        print(f"正在打开文件: {file_path}")
        
        # 构建请求数据
        open_file_json = {
            "Argument": file_path
        }
        
        # 发送打开文件请求
        response = midas_api.request("POST", "/doc/open", open_file_json)
        
        # 检查响应结果
        if response.get("message") == 'MIDAS CIVIL NX command complete':
            print("文件成功打开")
        else:
            print("打开文件失败:", response.get("message"))
            
        return response
        
    @staticmethod
    def analyze():
        """
        运行MIDAS模型分析
        
        返回:
        - dict: API响应结果
        
        示例:
        >>> response = MidasOperations.analyze()
        >>> print("分析完成" if response.get("message") == "MIDAS CIVIL NX command complete" else "分析失败")
        """
        print('开始运行计算')
        response = midas_api.request("POST", "/doc/anal", {})
        
        # 检查响应消息
        if isinstance(response, dict) and response.get("message") == "MIDAS CIVIL NX command complete":
            print('计算完成')
            return response
        else:
            print('计算失败')
            return None
        
    @staticmethod
    def save_file(file_path):
        """
        保存MIDAS模型文件
        
        参数:
        - file_path: str, 保存文件的完整路径，包括文件名和扩展名
        
        返回:
        - dict: API响应结果
        
        注意:
        - 如果目标路径已存在文件，将会覆盖
        - 建议使用.mcb作为文件扩展名
        
        示例:
        >>> MidasOperations.save_file("C:/Projects/bridge_new.mcb")
        """
        # 构建保存文件的请求数据
        saveas_json = {
            "Argument": file_path
        }
        
        # 发送保存请求
        response = midas_api.request("POST", "/doc/saveas", saveas_json)
        print('文件已保存' if response else '保存失败')
        return response 