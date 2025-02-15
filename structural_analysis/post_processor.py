"""后处理功能模块，提供结果提取和可视化功能，包括：
- 梁单元内力提取和绘图
- 梁单元应力提取和绘图
- 节点位移提取和绘图
支持General分析和施工阶段分析结果
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from .api import midas_api

class PostProcessor:
    """后处理基类，提供通用的绘图设置和数据处理功能"""
    
    def __init__(self):
        self._setup_plot_style()
        
    def _setup_plot_style(self):
        """设置统一的绘图样式"""
        plt.rcParams.update({
            'font.sans-serif': ['SimSun'],
            'font.family': 'serif',
            'font.serif': ['Times New Roman'],
            'font.size': 10
        })


class BeamForceProcessor(PostProcessor):
    """梁单元内力处理类"""
    
    def _process_elem_selection(self, elems):
        """
        处理单元选择的辅助方法
        
        参数:
        - elems: 可以是以下几种形式:
            - list/tuple: [101, 102, 103] (Method 1: specify each ID)
            - str: "101 to 105" (Method 2: specify ID Range)
            - str: "SG1" (Method 3: specify structure Group name)
            - None: 不指定单元，提取所有单元
            
        返回:
        - dict: 符合MIDAS接口要求的单元选择字典
        """
        if elems is None:
            return {}
            
        if isinstance(elems, (list, tuple)):
            # Method 1: specify each ID
            return {"KEY": list(map(int, elems))}
        elif isinstance(elems, str):
            if "to" in elems.lower():
                # Method 2: specify ID Range
                return {"TO": elems.strip()}
            else:
                # Method 3: specify structure Group name
                return {"STRUCTURE_GROUP_NAME": elems.strip()}
        else:
            raise ValueError("单元选择参数格式不正确。应为列表、范围字符串或结构组名称。")
    
    def extract_general(self, elems=None, load_case="comb1(CB)", **kwargs):
        """
        提取General分析的梁单元内力
        
        参数:
        - elems: 单元选择参数，支持三种方式:
            - list/tuple: [101, 102, 103] (指定具体单元ID)
            - str: "101 to 105" (指定单元范围)
            - str: "SG1" (指定结构组名称)
            - None: 不指定单元，提取所有单元
        - load_case: str, 荷载工况名称
        - kwargs: 可选参数，包括:
            - force_unit: str, 力单位
            - dist_unit: str, 距离单位
            - format_style: str, 数据格式
            - decimal_places: int, 小数位数
            - parts: list, 提取的部件列表
        """
        data = {
            "Argument": {
                "TABLE_NAME": "BeamForce",
                "TABLE_TYPE": "BEAMFORCE",
                "UNIT": {
                    "FORCE": kwargs.get("force_unit", "N"),
                    "DIST": kwargs.get("dist_unit", "mm")
                },
                "STYLES": {
                    "FORMAT": kwargs.get("format_style", "Fixed"),
                    "PLACE": kwargs.get("decimal_places", 6)
                },
                "COMPONENTS": [
                    "Elem", "Load", "Part", "Axial", "Shear-y", "Shear-z",
                    "Torsion", "Moment-y", "Moment-z", "Bi-Moment", "T-Moment", "W-Moment"
                ],
                "NODE_ELEMS": self._process_elem_selection(elems),
                "LOAD_CASE_NAMES": [load_case],
                "PARTS": kwargs.get("parts", ["PartI", "PartJ"])
            }
        }
        return midas_api.request("POST", "/post/table", data)

    def extract_construction(self, elems=None, load_case="合计(CS)", stages=None, **kwargs):
        """
        提取施工阶段的梁单元内力
        
        参数:
        - elems: 单元选择参数，支持三种方式:
            - list/tuple: [101, 102, 103] (指定具体单元ID)
            - str: "101 to 105" (指定单元范围)
            - str: "SG1" (指定结构组名称)
            - None: 不指定单元，提取所有单元
        - load_case: str, 荷载工况名称
        - stages: list, 施工阶段列表
        - kwargs: 其他可选参数(同extract_general)
        """
        data = {
            "Argument": {
                "TABLE_NAME": "BeamForce",
                "TABLE_TYPE": "BEAMFORCE",
                "UNIT": {
                    "FORCE": kwargs.get("force_unit", "N"),
                    "DIST": kwargs.get("dist_unit", "mm")
                },
                "STYLES": {
                    "FORMAT": kwargs.get("format_style", "Fixed"),
                    "PLACE": kwargs.get("decimal_places", 6)
                },
                "COMPONENTS": [
                    "Elem", "Load", "Stage", "Step", "Part", "Axial", "Shear-y", "Shear-z",
                    "Torsion", "Moment-y", "Moment-z", "Bi-Moment", "T-Moment", "W-Moment"
                ],
                "NODE_ELEMS": self._process_elem_selection(elems),
                "LOAD_CASE_NAMES": [load_case],
                "PARTS": kwargs.get("parts", ["PartI", "PartJ"]),
                "OPT_CS": True,
                "STAGE_STEP": stages
            }
        }
        return midas_api.request("POST", "/post/table", data)

    def process_general_results(self, raw_data):
        """处理General分析结果数据"""
        res_head = raw_data["BeamForce"]["HEAD"]
        res_data = raw_data["BeamForce"]["DATA"]
        df = pd.DataFrame(res_data, columns=res_head)
        
        # 转换数值列
        force_columns = [
            "Axial", "Shear-y", "Shear-z", "Torsion", 
            "Moment-y", "Moment-z", "Bi-Moment", "T-Moment", "W-Moment"
        ]
        for col in force_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        df["Elem"] = pd.to_numeric(df["Elem"])
        return df

    def process_construction_results(self, raw_data):
        """处理施工阶段结果数据，返回按阶段分组的DataFrame列表"""
        df = self.process_general_results(raw_data)
        return [group for _, group in df.groupby("Stage")]

    def plot_results(self, df, component="Moment-y", title=None, **kwargs):
        """
        绘制内力分布图
        
        参数:
        - df: DataFrame/list, 结果数据
        - component: str, 绘制的内力分量
        - title: str, 图表标题
        - kwargs: 其他绘图参数
        """
        if isinstance(df, list):  # 施工阶段结果
            fig, axes = plt.subplots(len(df), 1, 
                                   figsize=(10, 3*len(df)), 
                                   dpi=100)
            if len(df) == 1:
                axes = [axes]
                
            for i, stage_df in enumerate(df):
                stage_name = stage_df["Stage"].iloc[0]
                self._plot_single_result(stage_df, component, axes[i], 
                                       title=f"施工阶段 {stage_name} - {component} 分布图")
                
        else:  # General结果
            plt.figure(figsize=(10, 3), dpi=100)
            self._plot_single_result(df, component, plt.gca(), 
                                   title=title or f"{component} 分布图")
        
        plt.tight_layout()
        plt.show()
        
    def _plot_single_result(self, df, component, ax, title):
        """绘制单个结果图"""
        elem_values = df["Elem"].unique()
        comp_values = df[component].values
        
        x = np.append(elem_values, [elem_values[-1]+1])
        y = [comp_values[0]] + [
            (comp_values[i] + comp_values[i+1])/2 
            for i in range(1, len(comp_values)-2, 2)
        ] + [comp_values[-1]]
        
        ax.plot(x, y, marker="o", linestyle="-")
        ax.set_xlabel("单元编号", fontsize=10, family='SimSun')
        ax.set_ylabel(f"{component} (单位)", fontsize=10, family='SimSun')
        ax.set_title(title, fontsize=10, family='SimSun')
        ax.grid(True)
        
        # 设置刻度标签字体
        for label in ax.get_xticklabels() + ax.get_yticklabels():
            label.set_fontname("Times New Roman")


class BeamStressProcessor(PostProcessor):
    """梁单元应力处理类"""
    
    def _process_elem_selection(self, elems):
        """
        处理单元选择的辅助方法
        
        参数:
        - elems: 可以是以下几种形式:
            - list/tuple: [101, 102, 103] (Method 1: specify each ID)
            - str: "101 to 105" (Method 2: specify ID Range)
            - str: "SG1" (Method 3: specify structure Group name)
            - None: 不指定单元，提取所有单元
            
        返回:
        - dict: 符合MIDAS接口要求的单元选择字典
        """
        if elems is None:
            return {}
            
        if isinstance(elems, (list, tuple)):
            # Method 1: specify each ID
            return {"KEY": list(map(int, elems))}
        elif isinstance(elems, str):
            if "to" in elems.lower():
                # Method 2: specify ID Range
                return {"TO": elems.strip()}
            else:
                # Method 3: specify structure Group name
                return {"STRUCTURE_GROUP_NAME": elems.strip()}
        else:
            raise ValueError("单元选择参数格式不正确。应为列表、范围字符串或结构组名称。")

    def extract_general(self, elems=None, load_case="comb1(CB)", **kwargs):
        """
        提取General分析的梁单元应力
        
        参数:
        - elems: 单元选择参数，支持三种方式:
            - list/tuple: [101, 102, 103] (指定具体单元ID)
            - str: "101 to 105" (指定单元范围)
            - str: "SG1" (指定结构组名称)
            - None: 不指定单元，提取所有单元
        - load_case: str, 荷载工况名称
        - kwargs: 可选参数，包括:
            - force_unit: str, 力单位
            - dist_unit: str, 距离单位
            - format_style: str, 数据格式
            - decimal_places: int, 小数位数
            - parts: list, 提取的部件列表
        """
        data = {
            "Argument": {
                "TABLE_NAME": "BeamStress",
                "TABLE_TYPE": "BEAMSTRESS",
                "UNIT": {
                    "FORCE": kwargs.get("force_unit", "N"),
                    "DIST": kwargs.get("dist_unit", "mm")
                },
                "STYLES": {
                    "FORMAT": kwargs.get("format_style", "Fixed"),
                    "PLACE": kwargs.get("decimal_places", 6)
                },
                "COMPONENTS": [
                    "Elem", "Load", "Part", "Axial", "Shear-y", "Shear-z",
                    "Bend(+y)", "Bend(-y)", "Bend(+z)", "Bend(-z)", "Cb(min/max)",
                    "Cb1(-y+z)", "Cb2(+y+z)", "Cb3(+y-z)", "Cb4(-y-z)"
                ],
                "NODE_ELEMS": self._process_elem_selection(elems),
                "LOAD_CASE_NAMES": [load_case],
                "PARTS": kwargs.get("parts", ["PartI", "PartJ"])
            }
        }
        return midas_api.request("POST", "/post/table", data)

    def extract_construction(self, elems=None, load_case="合计(CS)", stages=None, **kwargs):
        """
        提取施工阶段的梁单元应力
        
        参数:
        - elems: 单元选择参数，支持三种方式:
            - list/tuple: [101, 102, 103] (指定具体单元ID)
            - str: "101 to 105" (指定单元范围)
            - str: "SG1" (指定结构组名称)
            - None: 不指定单元，提取所有单元
        - load_case: str, 荷载工况名称
        - stages: list, 施工阶段列表
        - kwargs: 其他可选参数(同extract_general)
        """
        data = {
            "Argument": {
                "TABLE_NAME": "BeamStress",
                "TABLE_TYPE": "BEAMSTRESS",
                "UNIT": {
                    "FORCE": kwargs.get("force_unit", "N"),
                    "DIST": kwargs.get("dist_unit", "mm")
                },
                "STYLES": {
                    "FORMAT": kwargs.get("format_style", "Fixed"),
                    "PLACE": kwargs.get("decimal_places", 6)
                },
                "COMPONENTS": [
                    "Elem", "Load", "Stage", "Step", "Part", "Axial", "Shear-y", "Shear-z",
                    "Bend(+y)", "Bend(-y)", "Bend(+z)", "Bend(-z)", "Cb(min/max)",
                    "Cb1(-y+z)", "Cb2(+y+z)", "Cb3(+y-z)", "Cb4(-y-z)"
                ],
                "NODE_ELEMS": self._process_elem_selection(elems),
                "LOAD_CASE_NAMES": [load_case],
                "PARTS": kwargs.get("parts", ["PartI", "PartJ"]),
                "OPT_CS": True,
                "STAGE_STEP": stages
            }
        }
        return midas_api.request("POST", "/post/table", data)

    def process_general_results(self, raw_data):
        """处理General分析结果数据"""
        res_head = raw_data["BeamStress"]["HEAD"]
        res_data = raw_data["BeamStress"]["DATA"]
        df = pd.DataFrame(res_data, columns=res_head)
        
        # 转换数值列
        stress_columns = [
            "Axial", "Shear-y", "Shear-z",
            "Bend(+y)", "Bend(-y)", "Bend(+z)", "Bend(-z)", "Cb(min/max)",
            "Cb1(-y+z)", "Cb2(+y+z)", "Cb3(+y-z)", "Cb4(-y-z)"
        ]
        for col in stress_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        df["Elem"] = pd.to_numeric(df["Elem"])
        return df

    def process_construction_results(self, raw_data):
        """处理施工阶段结果数据"""
        df = self.process_general_results(raw_data)
        return [group for _, group in df.groupby("Stage")]

    def plot_results(self, df, component="Bend(+y)", title=None, **kwargs):
        """
        绘制应力分布图
        
        参数:
        - df: DataFrame/list, 结果数据
        - component: str, 绘制的应力分量
        - title: str, 图表标题
        - kwargs: 其他绘图参数
        """
        if isinstance(df, list):  # 施工阶段结果
            fig, axes = plt.subplots(len(df), 1, 
                                   figsize=(10, 3*len(df)), 
                                   dpi=100)
            if len(df) == 1:
                axes = [axes]
                
            for i, stage_df in enumerate(df):
                stage_name = stage_df["Stage"].iloc[0]
                self._plot_single_result(stage_df, component, axes[i], 
                                       title=f"施工阶段 {stage_name} - {component} 分布图")
                
        else:  # General结果
            plt.figure(figsize=(10, 3), dpi=100)
            self._plot_single_result(df, component, plt.gca(), 
                                   title=title or f"{component} 分布图")
        
        plt.tight_layout()
        plt.show()
        
    def _plot_single_result(self, df, component, ax, title):
        """
        绘制单个应力结果图
        
        参数:
        - df: DataFrame, 包含应力数据
        - component: str, 要绘制的应力分量
        - ax: matplotlib.axes, 绘图轴对象
        - title: str, 图表标题
        """
        '''
        # 直接绘制单元编号和应力值
        ax.plot(df["Elem"], df[component], marker="o", linestyle="-")
        ax.set_xlabel("单元编号", fontsize=10, family='SimSun')
        ax.set_ylabel(f"{component} (单位)", fontsize=10, family='SimSun')
        ax.set_title(title, fontsize=10, family='SimSun')
        ax.grid(True)
        
        # 设置刻度标签字体
        ax.tick_params(axis='x', labelsize=10, labelrotation=0)
        ax.tick_params(axis='y', labelsize=10)
        for label in ax.get_xticklabels() + ax.get_yticklabels():
            label.set_fontname("Times New Roman")
        '''

        # 提取单元编号和应力分量
        elem_values = df["Elem"].values
        stress_values = df[component].values

        # 平滑处理：将每两点合并为一个点
        x = [(elem_values[i] + elem_values[i + 1]) / 2 for i in range(0, len(elem_values) - 1, 2)]
        y = [(stress_values[i] + stress_values[i + 1]) / 2 for i in range(0, len(stress_values) - 1, 2)]

        # 如果长度是奇数，保留最后一个点
        if len(elem_values) % 2 != 0:
            x.append(elem_values[-1])
            y.append(stress_values[-1])
    
        # 绘制应力分布图
        ax.plot(x, y, marker="o", linestyle="-")
        ax.set_xlabel("单元编号", fontsize=10, family='SimSun')
        ax.set_ylabel(f"{component} (单位)", fontsize=10, family='SimSun')
        ax.set_title(title, fontsize=10, family='SimSun')
        ax.grid(True)
        
        # 设置刻度标签字体
        ax.tick_params(axis='x', labelsize=10, labelrotation=0)
        ax.tick_params(axis='y', labelsize=10)
        for label in ax.get_xticklabels() + ax.get_yticklabels():
            label.set_fontname("Times New Roman")


class BeamStressProcessorSevenDOF(BeamStressProcessor):
    """七自由度梁单元应力处理类"""

    def extract_general(self, elems=None, load_case="comb1(CB)", **kwargs):
        """
        提取General分析的七自由度梁单元应力
        
        参数:
        - elems: list/None, 提取的单元范围
        - load_case: str, 荷载工况名称
        - kwargs: 可选参数，包括:
            - force_unit: str, 力单位
            - dist_unit: str, 距离单位
            - format_style: str, 数据格式
            - decimal_places: int, 小数位数
            - parts: list, 提取的部件列表
        """
        data = {
            "Argument": {
                "TABLE_NAME": "BeamStress(7DOF)",
                "TABLE_TYPE": "BEAMSTRESS7DOF",
                "UNIT": {
                    "FORCE": kwargs.get("force_unit", "N"),
                    "DIST": kwargs.get("dist_unit", "mm")
                },
                "STYLES": {
                    "FORMAT": kwargs.get("format_style", "Fixed"),
                    "PLACE": kwargs.get("decimal_places", 6)
                },
                "COMPONENTS": [
                    "Elem", "Load", "Part", "Axial", "Shear-y", "Shear-z", 
                    "Bend(+y)", "Bend(-y)", "Bend(+z)", "Bend(-z)", 
                    "Cb(min/max)", "Cb1(-y+z)", "Cb2(+y+z)", "Cb3(+y-z)", "Cb4(-y-z)"
                ],
                "NODE_ELEMS": {"TO": elems},
                "LOAD_CASE_NAMES": [load_case],
                "PARTS": kwargs.get("parts", ["PartI", "PartJ"])
            }
        }
        return midas_api.request("POST", "/post/table", data)

    def extract_construction(self, elems=None, load_case="合计(CS)", stages=None, **kwargs):
        """
        提取施工阶段的七自由度梁单元应力
        
        参数:
        - elems: list/None, 提取的单元范围
        - load_case: str, 荷载工况名称
        - stages: list, 施工阶段列表
        - kwargs: 其他可选参数(同extract_general)
        """
        data = {
            "Argument": {
                "TABLE_NAME": "BeamStress(7DOF)",
                "TABLE_TYPE": "BEAMSTRESS7DOF",
                "UNIT": {
                    "FORCE": kwargs.get("force_unit", "N"),
                    "DIST": kwargs.get("dist_unit", "mm")
                },
                "STYLES": {
                    "FORMAT": kwargs.get("format_style", "Fixed"),
                    "PLACE": kwargs.get("decimal_places", 6)
                },
                "COMPONENTS": [
                    "Elem", "Load", "Stage", "Step", "Part", "Axial", "Shear-y", "Shear-z", 
                    "Bend(+y)", "Bend(-y)", "Bend(+z)", "Bend(-z)", 
                    "Cb(min/max)", "Cb1(-y+z)", "Cb2(+y+z)", "Cb3(+y-z)", "Cb4(-y-z)"
                ],
                "NODE_ELEMS": {"TO": elems},
                "LOAD_CASE_NAMES": [load_case],
                "PARTS": kwargs.get("parts", ["PartI", "PartJ"]),
                "OPT_CS": True,
                "STAGE_STEP": stages
            }
        }
        return midas_api.request("POST", "/post/table", data)

    def process_general_results(self, raw_data):
        """处理General分析结果数据"""
        # 修正：使用正确的TABLE_NAME
        table_name = "BeamStress(7thDOF)"
        if table_name not in raw_data:
            raise KeyError(f"在结果数据中未找到 {table_name} 表")
            
        res_head = raw_data[table_name]["HEAD"]
        res_data = raw_data[table_name]["DATA"]
        df = pd.DataFrame(res_data, columns=res_head)
        
        # 转换数值列
        stress_columns = [
            "Axial", "Shear-y", "Shear-z", 
            "Bend(+y)", "Bend(-y)", "Bend(+z)", "Bend(-z)", 
            "Cb(min/max)", "Cb1(-y+z)", "Cb2(+y+z)", "Cb3(+y-z)", "Cb4(-y-z)"
        ]
        for col in stress_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        df["Elem"] = pd.to_numeric(df["Elem"])
        return df

    def process_construction_results(self, raw_data):
        """处理施工阶段结果数据"""
        df = self.process_general_results(raw_data)
        return [group for _, group in df.groupby("Stage")]

    def plot_results(self, df, component="Bend(+y)", title=None, **kwargs):
        """
        绘制应力分布图
        
        参数:
        - df: DataFrame/list, 结果数据
        - component: str, 绘制的应力分量
        - title: str, 图表标题
        - kwargs: 其他绘图参数
        """
        if isinstance(df, list):  # 施工阶段结果
            fig, axes = plt.subplots(len(df), 1, 
                                     figsize=(10, 3*len(df)), 
                                     dpi=100)
            if len(df) == 1:
                axes = [axes]
                
            for i, stage_df in enumerate(df):
                stage_name = stage_df["Stage"].iloc[0]
                self._plot_single_result(stage_df, component, axes[i], 
                                         title=f"施工阶段 {stage_name} - {component} 分布图")
                
        else:  # General结果
            plt.figure(figsize=(10, 3), dpi=100)
            self._plot_single_result(df, component, plt.gca(), 
                                     title=title or f"{component} 分布图")
        
        plt.tight_layout()
        plt.show()
        
    def _plot_single_result(self, df, component, ax, title):
        """
        绘制单个应力结果图
        
        参数:
        - df: DataFrame, 包含应力数据
        - component: str, 要绘制的应力分量
        - ax: matplotlib.axes, 绘图轴对象
        - title: str, 图表标题
        """
        # 提取单元编号和应力分量
        elem_values = df["Elem"].values
        stress_values = df[component].values

        # 平滑处理：将每两点合并为一个点
        x = [(elem_values[i] + elem_values[i + 1]) / 2 for i in range(0, len(elem_values) - 1, 2)]
        y = [(stress_values[i] + stress_values[i + 1]) / 2 for i in range(0, len(stress_values) - 1, 2)]

        # 如果长度是奇数，保留最后一个点
        if len(elem_values) % 2 != 0:
            x.append(elem_values[-1])
            y.append(stress_values[-1])
    
        # 绘制应力分布图
        ax.plot(x, y, marker="o", linestyle="-")
        ax.set_xlabel("单元编号", fontsize=10, family='SimSun')
        ax.set_ylabel(f"{component} (单位)", fontsize=10, family='SimSun')
        ax.set_title(title, fontsize=10, family='SimSun')
        ax.grid(True)
        
        # 设置刻度标签字体
        ax.tick_params(axis='x', labelsize=10, labelrotation=0)
        ax.tick_params(axis='y', labelsize=10)
        for label in ax.get_xticklabels() + ax.get_yticklabels():
            label.set_fontname("Times New Roman")

class TrussForceProcessor(PostProcessor):
    """桁架单元内力处理类"""
    
    def _process_elem_selection(self, elems):
        """
        处理单元选择的辅助方法
        
        参数:
        - elems: 可以是以下几种形式:
            - list/tuple: [33, 34, 35] (方法1: 指定具体单元ID)
            - str: "33 to 36" (方法2: 指定单元范围)
            - str: "SG1" (方法3: 指定结构组名称)
            - None: 不指定单元，提取所有单元
            
        返回:
        - dict: 符合MIDAS接口要求的单元选择字典
        """
        if elems is None:
            return {}
            
        if isinstance(elems, (list, tuple)):
            # Method 1: specify each ID
            return {"KEYS": list(map(int, elems))}
        elif isinstance(elems, str):
            if "to" in elems.lower():
                # Method 2: specify ID Range
                return {"TO": elems.strip()}
            else:
                # Method 3: specify structure Group name
                return {"STRUCTURE_GROUP_NAME": elems.strip()}
        else:
            raise ValueError("单元选择参数格式不正确。应为列表、范围字符串或结构组名称。")
    
    def extract_general(self, elems=None, load_case="comb1(CB)", **kwargs):
        """
        提取General分析的桁架单元内力
        
        参数:
        - elems: 单元选择参数，支持三种方式:
            - list/tuple: [33, 34, 35] (指定具体单元ID)
            - str: "33 to 36" (指定单元范围)
            - str: "SG1" (指定结构组名称)
            - None: 不指定单元，提取所有单元
        - load_case: str, 荷载工况名称
        - kwargs: 可选参数，包括:
            - force_unit: str, 力单位
            - dist_unit: str, 距离单位
            - format_style: str, 数据格式
            - decimal_places: int, 小数位数
        """
        data = {
            "Argument": {
                "TABLE_NAME": "TrussForce",
                "TABLE_TYPE": "TRUSSFORCE",
                "UNIT": {
                    "FORCE": kwargs.get("force_unit", "kN"),
                    "DIST": kwargs.get("dist_unit", "m")
                },
                "STYLES": {
                    "FORMAT": kwargs.get("format_style", "Fixed"),
                    "PLACE": kwargs.get("decimal_places", 6)
                },
                "COMPONENTS": ["Elem", "Load", "Force-I", "Force-J"],
                "NODE_ELEMS": self._process_elem_selection(elems),
                "LOAD_CASE_NAMES": [load_case]
            }
        }
        return midas_api.request("POST", "/post/table", data)

    def extract_construction(self, elems=None, load_case="合计(CS)", stages=None, **kwargs):
        """
        提取施工阶段的桁架单元内力
        
        参数:
        - elems: 单元选择参数，支持三种方式:
            - list/tuple: [33, 34, 35] (指定具体单元ID)
            - str: "33 to 36" (指定单元范围)
            - str: "SG1" (指定结构组名称)
            - None: 不指定单元，提取所有单元
        - load_case: str, 荷载工况名称
        - stages: list, 施工阶段列表
        - kwargs: 其他可选参数(同extract_general)
        """
        data = {
            "Argument": {
                "TABLE_NAME": "TrussForce",
                "TABLE_TYPE": "TRUSSFORCE",
                "UNIT": {
                    "FORCE": kwargs.get("force_unit", "kN"),
                    "DIST": kwargs.get("dist_unit", "m")
                },
                "STYLES": {
                    "FORMAT": kwargs.get("format_style", "Fixed"),
                    "PLACE": kwargs.get("decimal_places", 12)
                },
                "COMPONENTS": ["Elem", "Load", "Stage", "Step", "Force-I", "Force-J"],
                "NODE_ELEMS": self._process_elem_selection(elems),
                "LOAD_CASE_NAMES": [load_case],
                "OPT_CS": True,
                "STAGE_STEP": stages
            }
        }
        return midas_api.request("POST", "/post/table", data)

    def process_general_results(self, raw_data):
        """处理General分析结果数据"""
        res_head = raw_data["TrussForce"]["HEAD"]
        res_data = raw_data["TrussForce"]["DATA"]
        df = pd.DataFrame(res_data, columns=res_head)
        
        # 转换数值列
        force_columns = ["Force-I", "Force-J"]
        for col in force_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        df["Elem"] = pd.to_numeric(df["Elem"])
        return df

    def process_construction_results(self, raw_data):
        """处理施工阶段结果数据，返回按阶段分组的DataFrame列表"""
        df = self.process_general_results(raw_data)
        return [group for _, group in df.groupby("Stage")]

    def plot_results(self, df, component="Force-I", title=None, **kwargs):
        """
        绘制内力分布图
        
        参数:
        - df: DataFrame/list, 结果数据
        - component: str, 绘制的内力分量
        - title: str, 图表标题
        - kwargs: 其他绘图参数
        """
        if isinstance(df, list):  # 施工阶段结果
            fig, axes = plt.subplots(len(df), 1, 
                                   figsize=(10, 3*len(df)), 
                                   dpi=100)
            if len(df) == 1:
                axes = [axes]
                
            for i, stage_df in enumerate(df):
                stage_name = stage_df["Stage"].iloc[0]
                self._plot_single_result(stage_df, component, axes[i], 
                                         title=f"施工阶段 {stage_name} - {component} 分布图")
                
        else:  # General结果
            plt.figure(figsize=(10, 3), dpi=100)
            self._plot_single_result(df, component, plt.gca(), 
                                   title=title or f"{component} 分布图")
        
        plt.tight_layout()
        plt.show()

    def _plot_single_result(self, df, component, ax, title):
        """绘制单个结果图"""
        ax.plot(df["Elem"], df[component], marker="o", linestyle="-")
        ax.set_xlabel("单元编号", fontsize=10, family='SimSun')
        ax.set_ylabel(f"{component} (单位)", fontsize=10, family='SimSun')
        ax.set_title(title, fontsize=10, family='SimSun')
        ax.grid(True)
        
        # 设置刻度标签字体
        ax.tick_params(axis='x', labelsize=10, labelrotation=0)
        ax.tick_params(axis='y', labelsize=10)
        for label in ax.get_xticklabels() + ax.get_yticklabels():
            label.set_fontname("Times New Roman")

class TrussStressProcessor(PostProcessor):
    """桁架单元应力处理类"""
    
    def _process_elem_selection(self, elems):
        """
        处理单元选择的辅助方法
        
        参数:
        - elems: 可以是以下几种形式:
            - list/tuple: [33, 34, 35] (方法 1: 指定具体单元ID)
            - str: "33 to 36" (方法 2: 指定单元范围)
            - str: "SG1" (方法 3: 指定结构组名称)
            - None: 不指定单元，提取所有单元
            
        返回:
        - dict: 符合MIDAS接口要求的单元选择字典
        """
        if elems is None:
            return {}
            
        if isinstance(elems, (list, tuple)):
            # Method 1: specify each ID
            return {"KEYS": list(map(int, elems))}
        elif isinstance(elems, str):
            if "to" in elems.lower():
                # Method 2: specify ID Range
                return {"TO": elems.strip()}
            else:
                # Method 3: specify structure Group name
                return {"STRUCTURE_GROUP_NAME": elems.strip()}
        else:
            raise ValueError("单元选择参数格式不正确。应为列表、范围字符串或结构组名称。")

    def extract_general(self, elems=None, load_case="comb1(CB)", **kwargs):
        """
        提取General分析的桁架单元应力
        
        参数:
        - elems: 单元选择参数，支持三种方式:
            - list/tuple: [33, 34, 35] (指定具体单元ID)
            - str: "33 to 36" (指定单元范围)
            - str: "SG1" (指定结构组名称)
            - None: 不指定单元，提取所有单元
        - load_case: str, 荷载工况名称
        - kwargs: 可选参数，包括:
            - force_unit: str, 力单位
            - dist_unit: str, 距离单位
            - format_style: str, 数据格式
            - decimal_places: int, 小数位数
        """
        data = {
            "Argument": {
                "TABLE_NAME": "TrussStress",
                "TABLE_TYPE": "TRUSSSTRESS",
                "UNIT": {
                    "FORCE": kwargs.get("force_unit", "kN"),
                    "DIST": kwargs.get("dist_unit", "m")
                },
                "STYLES": {
                    "FORMAT": kwargs.get("format_style", "Fixed"),
                    "PLACE": kwargs.get("decimal_places", 12)
                },
                "COMPONENTS": ["Elem", "Load", "Stress-I", "Stress-J"],
                "NODE_ELEMS": self._process_elem_selection(elems),
                "LOAD_CASE_NAMES": [load_case]
            }
        }
        return midas_api.request("POST", "/post/table", data)

    def extract_construction(self, elems=None, load_case="合计(CS)", stages=None, **kwargs):
        """
        提取施工阶段的桁架单元应力
        
        参数:
        - elems: 单元选择参数，支持三种方式:
            - list/tuple: [33, 34, 35] (指定具体单元ID)
            - str: "33 to 36" (指定单元范围)
            - str: "SG1" (指定结构组名称)
            - None: 不指定单元，提取所有单元
        - load_case: str, 荷载工况名称
        - stages: list, 施工阶段列表
        - kwargs: 其他可选参数(同extract_general)
        """
        data = {
            "Argument": {
                "TABLE_NAME": "TrussStress",
                "TABLE_TYPE": "TRUSSSTRESS",
                "UNIT": {
                    "FORCE": kwargs.get("force_unit", "kN"),
                    "DIST": kwargs.get("dist_unit", "m")
                },
                "STYLES": {
                    "FORMAT": kwargs.get("format_style", "Fixed"),
                    "PLACE": kwargs.get("decimal_places", 12)
                },
                "COMPONENTS": ["Elem", "Load", "Stage", "Step", "Stress-I", "Stress-J"],
                "NODE_ELEMS": self._process_elem_selection(elems),
                "LOAD_CASE_NAMES": [load_case],
                "OPT_CS": True,
                "STAGE_STEP": stages
            }
        }
        return midas_api.request("POST", "/post/table", data)

    def process_general_results(self, raw_data):
        """处理General分析结果数据"""
        res_head = raw_data["TrussStress"]["HEAD"]
        res_data = raw_data["TrussStress"]["DATA"]
        df = pd.DataFrame(res_data, columns=res_head)
        
        # 转换数值列
        stress_columns = ["Stress-I", "Stress-J"]
        for col in stress_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        df["Elem"] = pd.to_numeric(df["Elem"])
        return df

    def process_construction_results(self, raw_data):
        """处理施工阶段结果数据，返回按阶段分组的DataFrame列表"""
        df = self.process_general_results(raw_data)
        return [group for _, group in df.groupby("Stage")]

    def plot_results(self, df, component="Stress-I", title=None, **kwargs):
        """
        绘制应力分布图
        
        参数:
        - df: DataFrame/list, 结果数据
        - component: str, 绘制的应力分量
        - title: str, 图表标题
        - kwargs: 其他绘图参数
        """
        if isinstance(df, list):  # 施工阶段结果
            fig, axes = plt.subplots(len(df), 1, 
                                     figsize=(10, 3*len(df)), 
                                     dpi=100)
            if len(df) == 1:
                axes = [axes]
                
            for i, stage_df in enumerate(df):
                stage_name = stage_df["Stage"].iloc[0]
                self._plot_single_result(stage_df, component, axes[i], 
                                         title=f"施工阶段 {stage_name} - {component} 分布图")
                
        else:  # General结果
            plt.figure(figsize=(10, 3), dpi=100)
            self._plot_single_result(df, component, plt.gca(), 
                                     title=title or f"{component} 分布图")
        
        plt.tight_layout()
        plt.show()

    def _plot_single_result(self, df, component, ax, title):
        """绘制单个结果图"""
        ax.plot(df["Elem"], df[component], marker="o", linestyle="-")
        ax.set_xlabel("单元编号", fontsize=10, family='SimSun')
        ax.set_ylabel(f"{component} (单位)", fontsize=10, family='SimSun')
        ax.set_title(title, fontsize=10, family='SimSun')
        ax.grid(True)
        
        # 设置刻度标签字体
        for label in ax.get_xticklabels() + ax.get_yticklabels():
            label.set_fontname("Times New Roman")

class CableForceProcessor(PostProcessor):
    """索单元内力处理类"""
    
    def _process_elem_selection(self, elems):
        """
        处理单元选择的辅助方法
        
        参数:
        - elems: 可以是以下几种形式:
            - list/tuple: [1, 2, 3] (方法 1: 指定具体单元ID)
            - str: "1 to 3" (方法 2: 指定单元范围)
            - str: "SG1" (方法 3: 指定结构组名称)
            - None: 不指定单元，提取所有单元
            
        返回:
        - dict: 符合MIDAS接口要求的单元选择字典
        """
        if elems is None:
            return {}
            
        if isinstance(elems, (list, tuple)):
            # Method 1: specify each ID
            return {"KEYS": list(map(int, elems))}
        elif isinstance(elems, str):
            if "to" in elems.lower():
                # Method 2: specify ID Range
                return {"TO": elems.strip()}
            else:
                # Method 3: specify structure Group name
                return {"STRUCTURE_GROUP_NAME": elems.strip()}
        else:
            raise ValueError("单元选择参数格式不正确。应为列表、范围字符串或结构组名称。")

    def extract_general(self, elems=None, load_case="comb1(CB)", **kwargs):
        """
        提取General分析的索单元内力
        
        参数:
        - elems: 单元选择参数，支持三种方式:
            - list/tuple: [101, 102, 103] (指定具体单元ID)
            - str: "101 to 105" (指定单元范围)
            - str: "SG1" (指定结构组名称)
            - None: 不指定单元，提取所有单元
        - load_case: str, 荷载工况名称
        - kwargs: 可选参数，包括:
            - force_unit: str, 力单位
            - dist_unit: str, 距离单位
            - format_style: str, 数据格式
            - decimal_places: int, 小数位数
        """
        data = {
            "Argument": {
                "TABLE_NAME": "CableForce",
                "TABLE_TYPE": "CABLEFORCE",
                "UNIT": {
                    "FORCE": kwargs.get("force_unit", "N"),
                    "DIST": kwargs.get("dist_unit", "mm")
                },
                "STYLES": {
                    "FORMAT": kwargs.get("format_style", "Fixed"),
                    "PLACE": kwargs.get("decimal_places", 6)
                },
                "COMPONENTS": [
                    "Elem", "NodeI", "NodeJ", "Load", "Step",
                    "Tension", "FX", "FY", "FZ", "Tension", "FX", "FY", "FZ"
                ],
                "NODE_ELEMS": self._process_elem_selection(elems),
                "LOAD_CASE_NAMES": [load_case]
            }
        }
        return midas_api.request("POST", "/post/table", data)

    def extract_construction(self, elems=None, load_case="合计(CS)", stages=None, **kwargs):
        """
        提取施工阶段的索单元内力
        
        参数:
        - elems: 单元选择参数，支持三种方式:
            - list/tuple: [101, 102, 103] (指定具体单元ID)
            - str: "101 to 105" (指定单元范围)
            - str: "SG1" (指定结构组名称)
            - None: 不指定单元，提取所有单元
        - load_case: str, 荷载工况名称
        - stages: list, 施工阶段列表
        - kwargs: 其他可选参数(同extract_general)
        """
        data = {
            "Argument": {
                "TABLE_NAME": "CableForce",
                "TABLE_TYPE": "CABLEFORCE",
                "UNIT": {
                    "FORCE": kwargs.get("force_unit", "N"),
                    "DIST": kwargs.get("dist_unit", "mm")
                },
                "STYLES": {
                    "FORMAT": kwargs.get("format_style", "Fixed"),
                    "PLACE": kwargs.get("decimal_places", 6)
                },
                "COMPONENTS": [
                    "Elem", "NodeI", "NodeJ", "Load", "Stage", "Step",
                    "Tension", "FX", "FY", "FZ", "Tension", "FX", "FY", "FZ"
                ],
                "NODE_ELEMS": self._process_elem_selection(elems),
                "LOAD_CASE_NAMES": [load_case],
                "OPT_CS": True,
                "STAGE_STEP": stages
            }
        }
        return midas_api.request("POST", "/post/table", data)

    def process_general_results(self, raw_data):
        """处理General分析结果数据"""
        res_head = raw_data["CableForce"]["HEAD"]
        res_data = raw_data["CableForce"]["DATA"]
        df = pd.DataFrame(res_data, columns=res_head)
        
        # 转换数值列
        force_columns = ["Tension", "FX", "FY", "FZ"]
        for col in force_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        df["Elem"] = pd.to_numeric(df["Elem"])
        return df

    def process_construction_results(self, raw_data):
        """处理施工阶段结果数据，返回按阶段分组的DataFrame列表"""
        df = self.process_general_results(raw_data)
        return [group for _, group in df.groupby("Stage")]

    def plot_results(self, df, component="Tension", title=None, **kwargs):
        """
        绘制索单元内力分布图
        
        参数:
        - df: DataFrame/list, 结果数据
        - component: str, 绘制的内力分量
        - title: str, 图表标题
        - kwargs: 其他绘图参数
        """
        if isinstance(df, list):  # 施工阶段结果
            fig, axes = plt.subplots(len(df), 1, 
                                     figsize=(10, 3*len(df)), 
                                     dpi=100)
            if len(df) == 1:
                axes = [axes]
                
            for i, stage_df in enumerate(df):
                stage_name = stage_df["Stage"].iloc[0]
                self._plot_single_result(stage_df, component, axes[i], 
                                         title=f"施工阶段 {stage_name} - {component} 分布图")
                
        else:  # General结果
            plt.figure(figsize=(10, 3), dpi=100)
            self._plot_single_result(df, component, plt.gca(), 
                                     title=title or f"{component} 分布图")
        
        plt.tight_layout()
        plt.show()

    def _plot_single_result(self, df, component, ax, title):
        """绘制单个结果图"""
        ax.plot(df["Elem"], df[component], marker="o", linestyle="-")
        ax.set_xlabel("单元编号", fontsize=10, family='SimSun')
        ax.set_ylabel(f"{component} (单位)", fontsize=10, family='SimSun')
        ax.set_title(title, fontsize=10, family='SimSun')
        ax.grid(True)
        
        # 设置刻度标签字体
        ax.tick_params(axis='x', labelsize=10, labelrotation=0)
        ax.tick_params(axis='y', labelsize=10)
        for label in ax.get_xticklabels() + ax.get_yticklabels():
            label.set_fontname("Times New Roman")

class CableEfficiencyProcessor(PostProcessor):
    """索效应处理类"""
    
    def _process_elem_selection(self, elems):
        """
        处理单元选择的辅助方法
        
        参数:
        - elems: 可以是以下几种形式:
            - list/tuple: [1, 2, 3] (方法 1: 指定具体单元ID)
            - str: "1 to 3" (方法 2: 指定单元范围)
            - str: "SG1" (方法 3: 指定结构组名称)
            - None: 不指定单元，提取所有单元
            
        返回:
        - dict: 符合MIDAS接口要求的单元选择字典
        """
        if elems is None:
            return {}
            
        if isinstance(elems, (list, tuple)):
            # Method 1: specify each ID
            return {"KEYS": list(map(int, elems))}
        elif isinstance(elems, str):
            if "to" in elems.lower():
                # Method 2: specify ID Range
                return {"TO": elems.strip()}
            else:
                # Method 3: specify structure Group name
                return {"STRUCTURE_GROUP_NAME": elems.strip()}
        else:
            raise ValueError("单元选择参数格式不正确。应为列表、范围字符串或结构组名称。")

    def extract_general(self, elems=None, load_case="comb1(CB)", **kwargs):
        """
        提取General分析的索效应信息
        
        参数:
        - elems: 单元选择参数，支持三种方式:
            - list/tuple: [1, 2, 3] (指定具体单元ID)
            - str: "1 to 3" (指定单元范围)
            - str: "SG1" (指定结构组名称)
            - None: 不指定单元，提取所有单元
        - load_case: str, 荷载工况名称
        - kwargs: 可选参数，包括:
            - force_unit: str, 力单位
            - dist_unit: str, 距离单位
            - format_style: str, 数据格式
            - decimal_places: int, 小数位数
        """
        data = {
            "Argument": {
                "TABLE_NAME": "CableEfficiency",
                "TABLE_TYPE": "CABLEEFFIENCY",
                "UNIT": {
                    "FORCE": kwargs.get("force_unit", "N"),
                    "DIST": kwargs.get("dist_unit", "mm")
                },
                "STYLES": {
                    "FORMAT": kwargs.get("format_style", "Fixed"),
                    "PLACE": kwargs.get("decimal_places", 6)
                },
                "COMPONENTS": [
                    "Elem", "NodeI", "NodeJ", "Load", "Step",
                    "ChordLength", "ExA", "Weight", "Tension",
                    "ExA(mod)", "Efficiency"
                ],
                "NODE_ELEMS": self._process_elem_selection(elems),
                "LOAD_CASE_NAMES": [load_case]
            }
        }
        return midas_api.request("POST", "/post/table", data)

    def extract_construction(self, elems=None, load_case="合计(CS)", stages=None, **kwargs):
        """
        提取施工阶段的索效应信息
        
        参数:
        - elems: 单元选择参数，支持三种方式:
            - list/tuple: [101, 102, 103] (指定具体单元ID)
            - str: "101 to 105" (指定单元范围)
            - str: "SG1" (指定结构组名称)
            - None: 不指定单元，提取所有单元
        - load_case: str, 荷载工况名称
        - stages: list, 施工阶段列表
        - kwargs: 其他可选参数(同extract_general)
        """
        data = {
            "Argument": {
                "TABLE_NAME": "CableEfficiency",
                "TABLE_TYPE": "CABLEEFFIENCY",
                "UNIT": {
                    "FORCE": kwargs.get("force_unit", "N"),
                    "DIST": kwargs.get("dist_unit", "mm")
                },
                "STYLES": {
                    "FORMAT": kwargs.get("format_style", "Fixed"),
                    "PLACE": kwargs.get("decimal_places", 6)
                },
                "COMPONENTS": [
                    "Elem", "NodeI", "NodeJ", "Load", "Stage", "Step",
                    "ChordLength", "ExA", "Weight", "Tension",
                    "ExA(mod)", "Efficiency"
                ],
                "NODE_ELEMS": self._process_elem_selection(elems),
                "LOAD_CASE_NAMES": [load_case],
                "OPT_CS": True,
                "STAGE_STEP": stages
            }
        }
        return midas_api.request("POST", "/post/table", data)

    def process_general_results(self, raw_data):
        """处理General分析结果数据"""
        res_head = raw_data["CableEfficiency"]["HEAD"]
        res_data = raw_data["CableEfficiency"]["DATA"]
        df = pd.DataFrame(res_data, columns=res_head)
        
        # 转换数值列
        numeric_columns = [
            "ChordLength", "ExA", "Weight", "Tension", 
            "ExA(mod)", "Efficiency"
        ]
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        df["Elem"] = pd.to_numeric(df["Elem"])
        return df

    def process_construction_results(self, raw_data):
        """处理施工阶段结果数据，返回按阶段分组的DataFrame列表"""
        df = self.process_general_results(raw_data)
        return [group for _, group in df.groupby("Stage")]


class CableConfigurationProcessor(PostProcessor):
    """索信息处理类"""
    
    def _process_elem_selection(self, elems):
        """
        处理单元选择的辅助方法
        
        参数:
        - elems: 可以是以下几种形式:
            - list/tuple: [1, 2, 3] (方法 1: 指定具体单元ID)
            - str: "1 to 3" (方法 2: 指定单元范围)
            - str: "SG1" (方法 3: 指定结构组名称)
            - None: 不指定单元，提取所有单元
            
        返回:
        - dict: 符合MIDAS接口要求的单元选择字典
        """
        if elems is None:
            return {}
            
        if isinstance(elems, (list, tuple)):
            # Method 1: specify each ID
            return {"KEYS": list(map(int, elems))}
        elif isinstance(elems, str):
            if "to" in elems.lower():
                # Method 2: specify ID Range
                return {"TO": elems.strip()}
            else:
                # Method 3: specify structure Group name
                return {"STRUCTURE_GROUP_NAME": elems.strip()}
        else:
            raise ValueError("单元选择参数格式不正确。应为列表、范围字符串或结构组名称。")

    def extract_general(self, elems=None, load_case="comb1(CB)", **kwargs):
        """
        提取General分析的索信息
        
        参数:
        - elems: 单元选择参数，支持三种方式:
            - list/tuple: [1, 2, 3] (指定具体单元ID)
            - str: "1 to 3" (指定单元范围)
            - str: "SG1" (指定结构组名称)
            - None: 不指定单元，提取所有单元
        - load_case: str, 荷载工况名称
        - kwargs: 可选参数，包括:
            - force_unit: str, 力单位
            - dist_unit: str, 距离单位
            - format_style: str, 数据格式
            - decimal_places: int, 小数位数
        """
        data = {
            "Argument": {
                "TABLE_NAME": "CableConfiguration",
                "TABLE_TYPE": "CABLECONFIG",
                "UNIT": {
                    "FORCE": kwargs.get("force_unit", "N"),
                    "DIST": kwargs.get("dist_unit", "mm")
                },
                "STYLES": {
                    "FORMAT": kwargs.get("format_style", "Fixed"),
                    "PLACE": kwargs.get("decimal_places", 6)
                },
                "COMPONENTS": [
                    "Elem", "NodeI", "NodeJ", "Load", "Step",
                    "TotalLength", "Elongation", "UnstrainedLength", "Sag",
                    "HorizontalDistance", "VerticalDistance", "Gradient",
                    "SkewAngle/IEnd", "SkewAngle/JEnd"
                ],
                "NODE_ELEMS": self._process_elem_selection(elems),
                "LOAD_CASE_NAMES": [load_case]
            }
        }
        return midas_api.request("POST", "/post/table", data)

    def extract_construction(self, elems=None, load_case="合计(CS)", stages=None, **kwargs):
        """
        提取施工阶段的索信息
        
        参数:
        - elems: 单元选择参数，支持三种方式:
            - list/tuple: [101, 102, 103] (指定具体单元ID)
            - str: "101 to 105" (指定单元范围)
            - str: "SG1" (指定结构组名称)
            - None: 不指定单元，提取所有单元
        - load_case: str, 荷载工况名称
        - stages: list, 施工阶段列表
        - kwargs: 其他可选参数(同extract_general)
        """
        data = {
            "Argument": {
                "TABLE_NAME": "CableConfiguration",
                "TABLE_TYPE": "CABLECONFIG",
                "UNIT": {
                    "FORCE": kwargs.get("force_unit", "N"),
                    "DIST": kwargs.get("dist_unit", "mm")
                },
                "STYLES": {
                    "FORMAT": kwargs.get("format_style", "Fixed"),
                    "PLACE": kwargs.get("decimal_places", 6)
                },
                "COMPONENTS": [
                    "Elem", "NodeI", "NodeJ", "Load", "Stage", "Step",
                    "TotalLength", "Elongation", "UnstrainedLength", "Sag",
                    "HorizontalDistance", "VerticalDistance", "Gradient"
                ],
                "NODE_ELEMS": self._process_elem_selection(elems),
                "LOAD_CASE_NAMES": [load_case],
                "OPT_CS": True,
                "STAGE_STEP": stages
            }
        }
        return midas_api.request("POST", "/post/table", data)

    def process_general_results(self, raw_data):
        """处理General分析结果数据"""
        res_head = raw_data["CableConfiguration"]["HEAD"]
        res_data = raw_data["CableConfiguration"]["DATA"]
        df = pd.DataFrame(res_data, columns=res_head)
        
        # 转换数值列
        numeric_columns = [
            "TotalLength", "Elongation", "UnstrainedLength", "Sag",
            "HorizontalDistance", "VerticalDistance", "Gradient",
            "SkewAngle/IEnd", "SkewAngle/JEnd"
        ]
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        df["Elem"] = pd.to_numeric(df["Elem"])
        return df

    def process_construction_results(self, raw_data):
        """处理施工阶段结果数据，返回按阶段分组的DataFrame列表"""
        df = self.process_general_results(raw_data)
        return [group for _, group in df.groupby("Stage")]


class DisplacementProcessor(PostProcessor):
    """节点位移处理类"""
    
    def _process_node_selection(self, nodes):
        """
        处理节点选择的辅助方法
        
        参数:
        - nodes: 可以是以下几种形式:
            - list/tuple: [101, 102, 103] (Method 1: specify each ID)
            - str: "101 to 105" (Method 2: specify ID Range)
            - str: "SG1" (Method 3: specify structure Group name)
            - None: 不指定节点，提取所有节点
            
        返回:
        - dict: 符合MIDAS接口要求的节点选择字典
        """
        if nodes is None:
            return {}
            
        if isinstance(nodes, (list, tuple)):
            # Method 1: specify each ID
            return {"KEY": list(map(int, nodes))}
        elif isinstance(nodes, str):
            if "to" in nodes.lower():
                # Method 2: specify ID Range
                return {"TO": nodes.strip()}
            else:
                # Method 3: specify structure Group name
                return {"STRUCTURE_GROUP_NAME": nodes.strip()}
        else:
            raise ValueError("节点选择参数格式不正确。应为列表、范围字符串或结构组名称。")
    
    def extract_general(self, nodes=None, load_case="comb1(CB)", **kwargs):
        """
        提取General分析的节点位移
        
        参数:
        - nodes: 节点选择参数，支持三种方式:
            - list/tuple: [101, 102, 103] (指定具体节点ID)
            - str: "101 to 105" (指定节点范围)
            - str: "SG1" (指定结构组名称)
            - None: 不指定节点，提取所有节点
        - load_case: str, 荷载工况名称
        - kwargs: 可选参数，包括:
            - force_unit: str, 力单位
            - dist_unit: str, 距离单位
            - format_style: str, 数据格式
            - decimal_places: int, 小数位数
        """
        data = {
            "Argument": {
                "TABLE_NAME": "Displacements(Global)",
                "TABLE_TYPE": "DISPLACEMENTG",
                "UNIT": {
                    "FORCE": kwargs.get("force_unit", "N"),
                    "DIST": kwargs.get("dist_unit", "mm")
                },
                "STYLES": {
                    "FORMAT": kwargs.get("format_style", "Scientific"),
                    "PLACE": kwargs.get("decimal_places", 3)
                },
                "COMPONENTS": [
                    "Node", "Load", "DX", "DY", "DZ", "RX", "RY", "RZ", "RW"
                ],
                "NODE_ELEMS": self._process_node_selection(nodes),
                "LOAD_CASE_NAMES": [load_case]
            }
        }
        return midas_api.request("POST", "/post/table", data)

    def extract_construction(self, nodes=None, load_case="合计(CS)", stages=None, **kwargs):
        """
        提取施工阶段的节点位移
        
        参数:
        - nodes: 节点选择参数，支持三种方式:
            - list/tuple: [101, 102, 103] (指定具体节点ID)
            - str: "101 to 105" (指定节点范围)
            - str: "SG1" (指定结构组名称)
            - None: 不指定节点，提取所有节点
        - load_case: str, 荷载工况名称
        - stages: list, 施工阶段列表
        - kwargs: 其他可选参数(同extract_general)
        - disp_opt: str, 位移选项("Accumulative", "Current", "Real")
        """
        data = {
            "Argument": {
                "TABLE_NAME": "Displacements(Global)",
                "TABLE_TYPE": "DISPLACEMENTG",
                "UNIT": {
                    "FORCE": kwargs.get("force_unit", "N"),
                    "DIST": kwargs.get("dist_unit", "mm")
                },
                "STYLES": {
                    "FORMAT": kwargs.get("format_style", "Scientific"),
                    "PLACE": kwargs.get("decimal_places", 6)
                },
                "COMPONENTS": [
                    "Node", "Load", "Stage", "Step",
                    "DX", "DY", "DZ", "RX", "RY", "RZ"
                ],
                "NODE_ELEMS": self._process_node_selection(nodes),
                "LOAD_CASE_NAMES": [load_case],
                "OPT_CS": True,
                "STAGE_STEP": stages,
                "DISP_OPT": kwargs.get("disp_opt", "Accumulative")
            }
        }
        return midas_api.request("POST", "/post/table", data)

    def process_general_results(self, raw_data):
        """处理General分析结果数据"""
        res_head = raw_data["Displacements(Global)"]["HEAD"]
        res_data = raw_data["Displacements(Global)"]["DATA"]
        df = pd.DataFrame(res_data, columns=res_head)
        
        # 转换数值列
        disp_columns = ["DX", "DY", "DZ", "RX", "RY", "RZ", "RW"]
        for col in disp_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        df["Node"] = pd.to_numeric(df["Node"])
        return df

    def process_construction_results(self, raw_data):
        """处理施工阶段结果数据，返回按阶段分组的DataFrame列表"""
        df = self.process_general_results(raw_data)
        return [group for _, group in df.groupby("Stage")]

    def plot_results(self, df, component="DZ", title=None, **kwargs):
        """
        绘制位移分布图
        
        参数:
        - df: DataFrame/list, 结果数据
        - component: str, 绘制的位移分量
        - title: str, 图表标题
        - kwargs: 其他绘图参数
        """
        if isinstance(df, list):  # 施工阶段结果
            fig, axes = plt.subplots(len(df), 1, 
                                   figsize=(10, 3*len(df)), 
                                   dpi=100)
            if len(df) == 1:
                axes = [axes]
                
            for i, stage_df in enumerate(df):
                stage_name = stage_df["Stage"].iloc[0]
                self._plot_single_result(stage_df, component, axes[i], 
                                       title=f"施工阶段 {stage_name} - {component} 分布图")
                
        else:  # General结果
            plt.figure(figsize=(10, 3), dpi=100)
            self._plot_single_result(df, component, plt.gca(), 
                                   title=title or f"{component} 分布图")
        
        plt.tight_layout()
        plt.show()
        
    def _plot_single_result(self, df, component, ax, title):
        """绘制单个位移结果图"""
        ax.plot(df["Node"], df[component], marker="o", linestyle="-")
        ax.set_xlabel("节点号", fontsize=10, family='SimSun')
        ax.set_ylabel(f"{component} (单位)", fontsize=10, family='SimSun')
        ax.set_title(title, fontsize=10, family='SimSun')
        ax.grid(True)
        
        # 设置刻度标签字体
        for label in ax.get_xticklabels() + ax.get_yticklabels():
            label.set_fontname("Times New Roman")

def create_processor(result_type):
    """
    工厂函数，创建对应的结果处理器
    
    参数:
    - result_type: str, 结果类型，支持:
        - "beam_force": 梁单元内力
        - "beam_stress": 梁单元应力
        - "beam_stress_7dof": 七自由度梁单元应力
        - "truss_force": 桁架单元内力
        - "truss_stress": 桁架单元应力
        - "cable_force": 索单元内力
        - "cable_efficiency": 索效应
        - "cable_config": 索信息
        - "displacement": 节点位移
    
    返回:
    - PostProcessor: 对应类型的结果处理器实例
    
    示例:
    >>> processor = create_processor("cable_force")
    >>> results = processor.extract_general(elems=[1, 2, 3])
    """
    processors = {
        # 原有处理器
        "beam_force": BeamForceProcessor,
        "beam_stress": BeamStressProcessor,
        "beam_stress_7dof": BeamStressProcessorSevenDOF,
        "displacement": DisplacementProcessor,
        
        # 新增处理器
        "truss_force": TrussForceProcessor,
        "truss_stress": TrussStressProcessor,
        "cable_force": CableForceProcessor,
        "cable_efficiency": CableEfficiencyProcessor,
        "cable_config": CableConfigurationProcessor
    }
    
    processor_class = processors.get(result_type)
    if processor_class is None:
        raise ValueError(
            f"不支持的结果类型: {result_type}\n"
            f"支持的类型包括: {', '.join(processors.keys())}"
        )
    
    return processor_class() 