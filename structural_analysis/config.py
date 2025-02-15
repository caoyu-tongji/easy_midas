"""配置模块,包含全局配置和常量"""

import winreg

class MidasConfig:
    def __init__(self):
        self.base_url, self.api_key = self._get_midas_connection()
        
    def _get_midas_connection(self):
        """从注册表获取MIDAS连接信息"""
        reg_path = r"SOFTWARE\MIDAS\CVLwNX_CH\CONNECTION"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
            uri = winreg.QueryValueEx(key, "URI")[0]
            port = winreg.QueryValueEx(key, "PORT")[0]
            api_key = winreg.QueryValueEx(key, "Key")[0]
            
            # 设置STARTUP
            try:
                winreg.SetValueEx(key, "STARTUP", 0, winreg.REG_DWORD, 1)
            except WindowsError:
                pass
                
        base_url = f"https://{uri}:{port}/civil"
        return base_url, api_key

# 全局配置实例
midas_config = MidasConfig() 