"""MIDAS API核心功能模块"""

import requests
from .config import midas_config

class MidasAPI:
    def __init__(self):
        self.base_url = midas_config.base_url
        self.headers = {
            "Content-Type": "application/json",
            "MAPI-Key": midas_config.api_key
        }
    
    def request(self, method, endpoint, data=None):
        """统一的API请求处理"""
        url = self.base_url + endpoint
        response = requests.request(
            method=method,
            url=url,
            headers=self.headers,
            json=data
        )
        print(f"{method} {endpoint} {response.status_code}")
        return response.json()

# 全局API实例        
midas_api = MidasAPI() 