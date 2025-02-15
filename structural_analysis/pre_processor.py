"""预处理功能模块"""

from .api import midas_api

class PreProcessor:
    """预处理功能类"""
    
    def __init__(self):
        """初始化预处理器"""
        self.node = None  # 节点处理器
        self.beam = None  # 梁单元处理器
        self.truss = None  # 桁架单元处理器
        self.cable = None  # 索单元处理器
        self.support = None  # 支撑处理器
        self.spring = None  # 弹性支撑处理器
        self.rigid_link = None  # 刚性连接处理器
        self.elastic_link = None  # 弹性连接处理器
    
    @staticmethod
    def set_units(force_unit, dist_unit):
        """设置单位"""
        data = {
            "Assign": {
                "1": {
                    "DIST": dist_unit,
                    "FORCE": force_unit
                }
            }
        }
        response = midas_api.request("PUT", "/db/unit", data)
        print(f"定义位移单位为{dist_unit}，力单位为{force_unit}")
        return response
        
    @staticmethod
    def define_material(material_id, **kwargs):
        """
        定义材料属性
        
        参数:
        - material_id: int, 材料编号
        - kwargs: 可包含以下参数:
            - TYPE: str, 材料类型 ("USER", "STEEL", "CONC", "SRC")
            - NAME: str, 材料名称
            - HE_SPEC: int, 传热特性
            - HE_COND: int, 热导率
            - PLMT: int, 填充材料属性
            - P_NAME: str, 填充材料名称
            - bMASS_DENS: bool, 是否具有质量密度属性
            - DAMP_RAT: float, 阻尼比
            - P_TYPE: int, 材料参数类型(1:规范参数, 2:各向同性, 3:各向异性)
            - ELAST: float, 弹性模量
            - POISN: float, 泊松比
            - THERMAL: float, 热膨胀系数
            - DEN: float, 容重
            - MASS: float, 质量
        """
        data = {
            "Assign": {
                str(material_id): {
                    "TYPE": kwargs.get("TYPE", "USER"),
                    "NAME": kwargs.get("NAME"),
                    "HE_SPEC": kwargs.get("HE_SPEC", 0),
                    "HE_COND": kwargs.get("HE_COND", 0),
                    "PLMT": kwargs.get("PLMT", 0),
                    "P_NAME": kwargs.get("P_NAME", ""),
                    "bMASS_DENS": kwargs.get("bMASS_DENS", True),
                    "DAMP_RAT": kwargs.get("DAMP_RAT", 0),
                    "PARAM": [{
                        "P_TYPE": kwargs.get("P_TYPE", 2),
                        "ELAST": kwargs.get("ELAST"),
                        "POISN": kwargs.get("POISN"),
                        "THERMAL": kwargs.get("THERMAL"),
                        "DEN": kwargs.get("DEN"),
                        "MASS": kwargs.get("MASS")
                    }]
                }
            }
        }
        response = midas_api.request("PUT", "/db/matl", data)
        print(f'材料ID{material_id} {kwargs.get("NAME")}修改完成')
        return response


class NodeProcessor:
    """节点处理类"""
    
    def query(self):
        """查询节点数据"""
        print('开始查询节点数据')
        response = midas_api.request("GET", "/db/NODE", {})
        if response:
            print("节点查询完成")
            return response
        print("节点查询失败")
        return None

    def create(self, node_data):
        """
        创建新节点
        
        参数:
        - node_data: dict, 节点数据(JSON格式)
        """
        print('开始创建节点')
        response = midas_api.request("POST", "/db/NODE", node_data)
        if response:
            print("节点创建完成")
            return response
        print("节点创建失败")
        return None

    def update(self, node_data):
        """
        更新节点数据
        
        参数:
        - node_data: dict, 节点数据(JSON格式)
        """
        print('开始更新节点数据')
        response = midas_api.request("PUT", "/db/NODE", node_data)
        if response:
            print("节点更新完成")
            return response
        print("节点更新失败")
        return None

    def delete_all(self):
        """删除所有节点"""
        print('开始删除所有节点')
        response = midas_api.request("DELETE", "/db/NODE", {})
        if response:
            print("节点删除完成")
            return response
        print("节点删除失败")
        return None

    def delete_single(self, node_id):
        """
        删除单个节点
        
        参数:
        - node_id: int/str, 节点编号
        """
        print(f'开始删除节点 {node_id}')
        response = midas_api.request("DELETE", f"/db/NODE/{node_id}")
        return response


class ElementProcessor:
    """单元处理基类"""
    
    def __init__(self, element_type):
        """
        初始化函数
        
        参数:
        - element_type: str, 单元类型 ("BEAM", "TRUSS", "TENSTR")
        """
        self.element_type = element_type

    def query(self):
        """查询单元数据"""
        print(f'开始查询{self.element_type}单元')
        return midas_api.request("GET", "/db/ELEM", {})

    def create(self, element_id, matl, sect, nodes, angle=0, **kwargs):
        """
        创建新单元
        
        参数:
        - element_id: int, 单元编号
        - matl: int, 材料ID
        - sect: int, 截面ID
        - nodes: list, 节点编号列表
        - angle: int, 单元旋转角度(默认0)
        - kwargs: 其他参数(用于Cable单元)
        """
        element_data = self._prepare_element_data(element_id, matl, sect, nodes, angle, **kwargs)
        print(f'开始创建{self.element_type}单元，编号 {element_id}')
        return midas_api.request("PUT", "/db/ELEM", element_data)

    def update(self, element_id, matl, sect, nodes, angle=0, **kwargs):
        """更新单元数据，参数同create方法"""
        return self.create(element_id, matl, sect, nodes, angle, **kwargs)

    def delete_all(self):
        """删除所有单元"""
        print(f'开始删除所有{self.element_type}单元')
        return midas_api.request("DELETE", "/db/ELEM")

    def delete_single(self, element_id):
        """删除单个单元"""
        print(f'开始删除单个{self.element_type}单元，编号 {element_id}')
        return midas_api.request("DELETE", f"/db/ELEM/{element_id}")

    def _prepare_element_data(self, element_id, matl, sect, nodes, angle, **kwargs):
        """准备单元数据"""
        data = {
            "Assign": {
                str(element_id): {
                    "TYPE": self.element_type,
                    "MATL": matl,
                    "SECT": sect,
                    "NODE": nodes,
                    "ANGLE": angle
                }
            }
        }
        
        # 处理Cable单元的特殊参数
        if self.element_type == "TENSTR":
            element_data = data["Assign"][str(element_id)]
            element_data["STYPE"] = kwargs.get("stype", 3)
            element_data["CABLE"] = kwargs.get("cable_type", 3)
            
            if kwargs.get("cable_type") == 3:
                element_data["NON_LEN"] = kwargs.get("non_len", 1.0)
            elif kwargs.get("cable_type") in [1, 2]:
                element_data["TENS"] = kwargs.get("tens", 0)
                
        return data


class BeamElement(ElementProcessor):
    """梁单元处理类"""
    def __init__(self):
        super().__init__("BEAM")


class TrussElement(ElementProcessor):
    """桁架单元处理类"""
    def __init__(self):
        super().__init__("TRUSS")


class CableElement(ElementProcessor):
    """索单元处理类"""
    def __init__(self):
        super().__init__("TENSTR")


class BoundaryConditionProcessor:
    """
    边界条件处理基类，提供边界条件的基本操作功能
    
    属性:
    - cons_json: dict, 存储边界条件分配的数据结构
    """
    
    def __init__(self):
        """初始化边界条件处理器"""
        self.cons_json = {"Assign": {}}

    def query(self):
        """
        查询所有边界条件（GET操作）
        
        返回:
        - dict: 边界条件数据
        """
        print('开始查询边界条件数据')
        response = midas_api.request("GET", "/db/cons", {})
        if response:
            print("边界条件查询完成")
            return response
        print("边界条件查询失败")
        return None

    def add_constraint(self, node_id, constraint_str, group_name=""):
        """
        为指定节点添加边界条件（POST操作）
        
        参数:
        - node_id: int/str, 节点编号
        - constraint_str: str, 边界条件字符串，例如"1111000"
            - 1表示约束
            - 0表示自由
            - 从左到右分别对应：UX, UY, UZ, RX, RY, RZ, RW
        - group_name: str, 约束条件组名，默认为"Service"
        
        返回:
        - bool: 操作是否成功
        """
        try:
            node_id = str(node_id)
            # 创建固定格式的约束条件
            self.cons_json["Assign"][node_id] = {
                "ITEMS": [
                    {
                        "ID": 1,  # ID固定为1
                        "GROUP_NAME": group_name,
                        "CONSTRAINT": constraint_str
                    }
                ]
            }
            print(f"节点 {node_id} 添加边界条件成功: {constraint_str}")
            return True
        except Exception as e:
            print(f"添加边界条件失败: {str(e)}")
            return False

    def update_constraint(self, node_id, constraint_str, group_name=""):
        """
        更新指定节点的边界条件（PUT操作）
        
        参数:
        - node_id: int/str, 节点编号
        - constraint_str: str, 新的边界条件字符串
        - group_name: str, 约束条件组名，默认为"Service"
        
        返回:
        - bool: 操作是否成功
        """
        try:
            node_id = str(node_id)
            if node_id not in self.cons_json["Assign"]:
                print(f"节点 {node_id} 不存在边界条件，无法更新")
                return False
                
            # 更新约束条件，保持ID为1
            self.cons_json["Assign"][node_id] = {
                "ITEMS": [
                    {
                        "ID": 1,
                        "GROUP_NAME": group_name,
                        "CONSTRAINT": constraint_str
                    }
                ]
            }
            print(f"节点 {node_id} 边界条件更新成功: {constraint_str}")
            return True
        except Exception as e:
            print(f"更新边界条件失败: {str(e)}")
            return False

    def delete_all(self):
        """
        删除所有边界条件（DELETE操作）
        
        返回:
        - dict: API响应结果
        """
        print('开始删除所有边界条件')
        response = midas_api.request("DELETE", "/db/cons", {})
        if response:
            print("边界条件删除完成")
            self.cons_json["Assign"].clear()  # 清空本地存储
            return response
        print("边界条件删除失败")
        return None

    def delete_single(self, node_id):
        """
        删除单个节点的边界条件（DELETE操作）
        
        参数:
        - node_id: int/str, 节点编号
        
        返回:
        - dict: API响应结果
        """
        print(f'开始删除节点 {node_id} 的边界条件')
        response = midas_api.request("DELETE", f"/db/cons/{node_id}")
        if response:
            if str(node_id) in self.cons_json["Assign"]:
                del self.cons_json["Assign"][str(node_id)]  # 更新本地存储
            print(f"节点 {node_id} 的边界条件删除完成")
            return response
        print(f"节点 {node_id} 的边界条件删除失败")
        return None

    def apply_constraints(self):
        """
        将边界条件应用到模型
        
        返回:
        - dict: API响应结果
        """
        response = midas_api.request("PUT", "/db/cons", self.cons_json)
        if response:
            print("边界条件应用成功")
        else:
            print("边界条件应用失败")
        return response

class SupportProcessor(BoundaryConditionProcessor):
    """
    一般支撑处理类，提供节点支撑的添加、修改、删除功能
    
    继承:
    - BoundaryConditionProcessor: 边界条件处理基类
    """
    
    def add_support(self, node_id, dx=0, dy=0, dz=0, rx=0, ry=0, rz=0, rw=0):
        """
        为单个节点添加支撑条件（POST操作）
        
        参数:
        - node_id: int/str, 节点编号
        - dx, dy, dz: int, 平动约束(0:自由, 1:约束)
        - rx, ry, rz, rw: int, 转动约束(0:自由, 1:约束)
        
        返回:
        - bool: 操作是否成功
        """
        constraint_str = f"{dx}{dy}{dz}{rx}{ry}{rz}{rw}"
        return self.add_constraint(node_id, constraint_str)

    def update_support(self, node_id, dx=0, dy=0, dz=0, rx=0, ry=0, rz=0, rw=0):
        """
        更新节点支撑
        
        参数同add_support方法
        
        返回:
        - bool: 操作是否成功
        """
        constraint_str = f"{dx}{dy}{dz}{rx}{ry}{rz}{rw}"
        return self.update_constraint(node_id, constraint_str)

    def delete_support(self, node_id=None):
        """
        删除节点支撑
        
        参数:
        - node_id: int/str/None, 节点编号，None表示删除所有支撑
        
        返回:
        - bool: 操作是否成功
        """
        return self.delete_constraint(node_id)

    def apply_supports(self):
        """
        应用所有支撑设置
        
        返回:
        - dict: API响应结果
        """
        return self.apply_constraints()

    def query_supports(self):
        """
        查询所有支撑条件
        
        返回:
        - dict: 支撑条件数据
        """
        return self.query()

    def delete_all_supports(self):
        """
        删除所有支撑条件
        
        返回:
        - dict: API响应结果
        """
        return self.delete_all()

    def delete_support(self, node_id):
        """
        删除指定节点的支撑条件
        
        参数:
        - node_id: int/str, 节点编号
        
        返回:
        - dict: API响应结果
        """
        return self.delete_single(node_id)

class PointSpringProcessor(BoundaryConditionProcessor):
    """节点弹性支撑处理类
    提供弹性支撑的添加、修改、删除功能
    """
    
    def query(self):
        """查询弹性支撑数据"""
        print('开始查询弹性支撑数据')
        response = midas_api.request("GET", "/db/NSPR", {})
        if response:
            print("弹性支撑查询完成")
            return response
        print("弹性支撑查询失败")
        return None

    def add_linear_spring(self, node_id, damping=False, Cr=None, group_name="", F_S=None, SDR=None):
        """
        为单个节点添加线性弹性支撑条件（POST操作）
        
        参数:
        - node_id: int/str, 节点编号
        - damping: bool, 是否开启阻尼，默认为 False
        - Cr: list, 阻尼系数，长度为6的列表，默认为 [0, 0, 0, 0, 0, 0]
        - group_name: str, 约束条件组名，默认为空字符串 ""
        - F_S: list, 是否固定的6个方向的列表，默认为 [False, False, False, False, False, False]
        - SDR: list, 每个方向的刚度，默认为 [0, 0, 0, 0, 0, 0]
        
        返回:
        - bool: 操作是否成功
        """
        spring_data = self._prepare_linear_spring_data(
            node_id, damping, Cr, group_name, F_S, SDR
        )
        print(f'开始添加节点 {node_id} 的线性弹性支撑')
        response = midas_api.request("POST", "/db/NSPR", spring_data)
        if response:
            print(f"节点 {node_id} 添加线性弹性支撑成功")
            return True
        print(f"节点 {node_id} 添加线性弹性支撑失败")
        return False

    def add_nonlinear_spring(self, node_id, spring_type, direction, stiffness, group_name="", DV=None):
        """
        添加非线性弹性支撑
        
        参数:
        - node_id: int/str, 节点编号
        - spring_type: str, 支撑类型("COMP"/"TENS")，仅受压以及仅受拉
        - direction: int, 作用方向(0~6)，0~5分别代表Dx(+)、Dx(-)、Dy(+)、Dy(-)、Dz(+)、Dz(-)，6代表向量
        - stiffness: float, 刚度值
        - group_name: str, 约束条件组名
        - DV: list, 方向向量[x,y,z]
        """
        spring_data = self._prepare_nonlinear_spring_data(
            node_id, spring_type, direction, stiffness, group_name, DV
        )
        print(f'开始添加节点 {node_id} 的{spring_type}弹性支撑')
        response = midas_api.request("POST", "/db/NSPR", spring_data)
        if response:
            print(f"节点 {node_id} 添加{spring_type}弹性支撑成功")
            return True
        print(f"节点 {node_id} 添加{spring_type}弹性支撑失败")
        return False

    def update(self, node_id, spring_data):
        """
        更新弹性支撑数据
        
        参数:
        - node_id: int/str, 节点编号
        - spring_data: dict, 支撑数据
        """
        update_data = {"Assign": {str(node_id): spring_data}}
        print(f'开始更新节点 {node_id} 的弹性支撑')
        response = midas_api.request("PUT", "/db/NSPR", update_data)
        if response:
            print(f"节点 {node_id} 弹性支撑更新成功")
            return True
        print(f"节点 {node_id} 弹性支撑更新失败")
        return False

    def delete_all(self):
        """删除所有弹性支撑"""
        print('开始删除所有弹性支撑')
        response = midas_api.request("DELETE", "/db/NSPR", {})
        if response:
            print("所有弹性支撑删除完成")
            return response
        print("删除所有弹性支撑失败")
        return None

    def delete_single(self, node_id):
        """
        删除单个节点的弹性支撑
        
        参数:
        - node_id: int/str, 节点编号
        """
        print(f'开始删除节点 {node_id} 的弹性支撑')
        response = midas_api.request("DELETE", f"/db/NSPR/{node_id}")
        if response:
            print(f"节点 {node_id} 的弹性支撑删除成功")
            return response
        print(f"节点 {node_id} 的弹性支撑删除失败")
        return None

    def _prepare_linear_spring_data(self, node_id, damping, Cr, group_name, F_S, SDR):
        """准备线性弹性支撑数据"""
        return {
            "Assign": {
                str(node_id): {
                    "ITEMS": [{
                        "ID": 1,
                        "TYPE": "LINEAR",
                        "F_S": F_S or [False] * 6,
                        "SDR": SDR or [0] * 6,
                        "DAMPING": damping,
                        "Cr": Cr or [0] * 6,
                        "GROUP_NAME": group_name
                    }]
                }
            }
        }

    def _prepare_nonlinear_spring_data(self, node_id, spring_type, direction, stiffness, group_name, DV):
        """准备非线性弹性支撑数据"""
        return {
            "Assign": {
                str(node_id): {
                    "ITEMS": [{
                        "ID": 1,
                        "TYPE": spring_type,
                        "GROUP_NAME": group_name,
                        "DIR": direction,
                        "DV": DV or [0, 0, 0],
                        "STIFF": stiffness
                    }]
                }
            }
        }

class RigidLinkProcessor(BoundaryConditionProcessor):
    """
    刚性连接处理类，提供刚性连接的添加、修改、删除功能
    
    继承:
    - BoundaryConditionProcessor: 边界条件处理基类
    """
    
    def query(self):
        """
        查询刚性连接数据（GET操作）
        
        返回:
        - dict: 刚性连接数据，如果请求失败返回None
        """
        print('开始查询刚性连接数据')
        response = midas_api.request("GET", "/db/RIGD", {})
        if response:
            print("刚性连接查询完成")
            return response
        print("刚性连接查询失败")
        return None

    def add_rigid_link(self, node_id, dof, s_node, group_name=""):
        """
        为单个节点添加刚性连接条件（POST操作）
    
        参数:
        - node_id: int/str, 主节点编号
        - dof: str, 自由度组合字符串，6位数字表示
            从左到右依次为：DX, DY, DZ, RX, RY, RZ
            每位取值：1(刚性), 0(自由)
            例如："111000"表示三个平动刚性，三个转动自由
        - s_node: list, 从节点编号列表
        - group_name: str, 约束条件组名，默认为空字符串
        
        返回:
        - bool: 操作是否成功
        """
        try:
            rigid_link_data = self._prepare_rigid_link_data(node_id, dof, s_node, group_name)
            print(f'开始添加节点 {node_id} 的刚性连接')
            response = midas_api.request("POST", "/db/RIGD", rigid_link_data)
            if response:
                print(f"节点 {node_id} 添加刚性连接成功")
                return True
            print(f"节点 {node_id} 添加刚性连接失败")
            return False
        except Exception as e:
            print(f"添加刚性连接失败: {str(e)}")
            return False

    def update_rigid_link(self, node_id, dof, s_node, group_name=""):
        """
        更新节点的刚性连接（PUT操作）
        
        参数:
        - node_id: int/str, 主节点编号
        - dof: str, 自由度组合字符串
        - s_node: list, 从节点编号列表
        - group_name: str, 约束条件组名，默认为空字符串
        
        返回:
        - bool: 操作是否成功
        """
        try:
            rigid_link_data = self._prepare_rigid_link_data(node_id, dof, s_node, group_name)
            print(f'开始更新节点 {node_id} 的刚性连接')
            response = midas_api.request("PUT", "/db/RIGD", rigid_link_data)
            if response:
                print(f"节点 {node_id} 刚性连接更新成功")
                return True
            print(f"节点 {node_id} 刚性连接更新失败")
            return False
        except Exception as e:
            print(f"更新刚性连接失败: {str(e)}")
            return False

    def delete_all(self):
        """
        删除所有刚性连接（DELETE操作）
        
        返回:
        - dict: API响应结果，如果请求失败返回None
        """
        print('开始删除所有刚性连接')
        response = midas_api.request("DELETE", "/db/RIGD", {})
        if response:
            print("所有刚性连接删除完成")
            return response
        print("删除所有刚性连接失败")
        return None

    def delete_single(self, node_id):
        """
        删除单个节点的刚性连接（DELETE操作）
        
        参数:
        - node_id: int/str, 主节点编号
        
        返回:
        - dict: API响应结果，如果请求失败返回None
        """
        print(f'开始删除节点 {node_id} 的刚性连接')
        response = midas_api.request("DELETE", f"/db/RIGD/{node_id}")
        if response:
            print(f"节点 {node_id} 的刚性连接删除成功")
            return response
        print(f"节点 {node_id} 的刚性连接删除失败")
        return None

    def _prepare_rigid_link_data(self, node_id, dof, s_node, group_name=""):
        """
        准备刚性连接数据
        
        参数:
        - node_id: int/str, 主节点编号
        - dof: str, 自由度组合字符串
        - s_node: list, 从节点编号列表
        - group_name: str, 约束条件组名
        
        返回:
        - dict: 刚性连接数据结构
        """
        return {
            "Assign": {
                str(node_id): {
                    "ITEMS": [{
                        "ID": 1,
                        "GROUP_NAME": group_name,
                        "DOF": dof,
                        "S_NODE": s_node
                    }]
                }
            }
        }


class ElasticLinkProcessor(BoundaryConditionProcessor):
    """
    弹性连接处理类，提供弹性连接的添加、修改、删除功能
    
    继承:
    - BoundaryConditionProcessor: 边界条件处理基类
    
    支持的连接类型:
    - 一般类型 (General Type)
    - 刚性类型 (Rigid Type)
    - 仅受拉类型 (Tension-only Type)
    - 仅受压类型 (Compression-only Type)
    """

    def query(self):
        """
        查询所有弹性连接数据（GET操作）
        
        返回:
        - dict: 弹性连接数据，如果请求失败返回None
        """
        print('开始查询弹性连接数据')
        response = midas_api.request("GET", "/db/ELNK", {})
        if response:
            print("弹性连接查询完成")
            return response
        print("弹性连接查询失败")
        return None

    def add_general_link(self, link_id, node_pair, angle=0, rs=None, sdr=None, bshear=True, dr=None, bngr_name=""):
        """
        添加一般弹性连接（POST操作）
        
        参数:
        - link_id: int/str, 弹性连接编号
        - node_pair: list, 连接的节点对[起始节点, 终止节点]
        - angle: int, 局部坐标系角度，单位为度，默认为0
        - rs: list, 约束释放状态，长度为6的布尔列表
            [DX, DY, DZ, RX, RY, RZ]，True表示约束，False表示释放
            默认全部释放[False, False, False, False, False, False]
        - sdr: list, 各方向刚度值，长度为6的列表
            [KX, KY, KZ, KRX, KRY, KRZ]，默认为[0, 0, 0, 0, 0, 0]
        - bshear: bool, 是否考虑剪切变形，默认为True
        - dr: list, 剪切弹簧位置比例[r1, r2]，默认为[0.5, 0.5]
        - bngr_name: str, 连接组名称，默认为空字符串
        
        返回:
        - bool: 操作是否成功
        """
        try:
            data = self._prepare_general_link_data(
                link_id, node_pair, angle, rs, sdr, bshear, dr, bngr_name
            )
            print(f'开始添加一般弹性连接，ID: {link_id}')
            response = midas_api.request("POST", "/db/ELNK", data)
            if response:
                print(f"一般弹性连接 {link_id} 添加成功")
                return True
            print(f"一般弹性连接 {link_id} 添加失败")
            return False
        except Exception as e:
            print(f"添加一般弹性连接失败: {str(e)}")
            return False

    def add_rigid_link(self, link_id, node_pair, angle=0, bngr_name=""):
        """
        添加刚性连接（POST操作）
        
        参数:
        - link_id: int/str, 弹性连接编号
        - node_pair: list, 连接的节点对[起始节点, 终止节点]
        - angle: int, 局部坐标系角度，单位为度，默认为0
        - bngr_name: str, 连接组名称，默认为空字符串
        
        返回:
        - bool: 操作是否成功
        """
        try:
            data = self._prepare_rigid_link_data(link_id, node_pair, angle, bngr_name)
            print(f'开始添加刚性连接，ID: {link_id}')
            response = midas_api.request("POST", "/db/ELNK", data)
            if response:
                print(f"刚性连接 {link_id} 添加成功")
                return True
            print(f"刚性连接 {link_id} 添加失败")
            return False
        except Exception as e:
            print(f"添加刚性连接失败: {str(e)}")
            return False

    def add_nonlinear_link(self, link_id, node_pair, link_type, angle=0, sdr=None, bngr_name=""):
        """
        添加非线性连接（POST操作）
        
        参数:
        - link_id: int/str, 弹性连接编号
        - node_pair: list, 连接的节点对[起始节点, 终止节点]
        - link_type: str, 连接类型("TENS"/"COMP")
        - angle: int, 局部坐标系角度，单位为度，默认为0
        - sdr: list, 刚度值列表，长度为6，仅第一个值有效，默认为[0, 0, 0, 0, 0, 0]
        - bngr_name: str, 连接组名称，默认为空字符串
        
        返回:
        - bool: 操作是否成功
        """
        try:
            data = self._prepare_nonlinear_link_data(
                link_id, node_pair, link_type, angle, sdr, bngr_name
            )
            print(f'开始添加{link_type}连接，ID: {link_id}')
            response = midas_api.request("POST", "/db/ELNK", data)
            if response:
                print(f"{link_type}连接 {link_id} 添加成功")
                return True
            print(f"{link_type}连接 {link_id} 添加失败")
            return False
        except Exception as e:
            print(f"添加{link_type}连接失败: {str(e)}")
            return False

    def update_link(self, link_id, data):
        """
        更新弹性连接（PUT操作）
        
        参数:
        - link_id: int/str, 弹性连接编号
        - data: dict, 更新的连接数据
        
        返回:
        - bool: 操作是否成功
        """
        try:
            update_data = {"Assign": {str(link_id): data}}
            print(f'开始更新弹性连接，ID: {link_id}')
            response = midas_api.request("PUT", "/db/ELNK", update_data)
            if response:
                print(f"弹性连接 {link_id} 更新成功")
                return True
            print(f"弹性连接 {link_id} 更新失败")
            return False
        except Exception as e:
            print(f"更新弹性连接失败: {str(e)}")
            return False

    def delete_all(self):
        """
        删除所有弹性连接（DELETE操作）
        
        返回:
        - dict: API响应结果，如果请求失败返回None
        """
        print('开始删除所有弹性连接')
        response = midas_api.request("DELETE", "/db/ELNK", {})
        if response:
            print("所有弹性连接删除完成")
            return response
        print("删除所有弹性连接失败")
        return None

    def delete_single(self, link_id):
        """
        删除单个弹性连接（DELETE操作）
        
        参数:
        - link_id: int/str, 弹性连接编号
        
        返回:
        - dict: API响应结果，如果请求失败返回None
        """
        print(f'开始删除弹性连接，ID: {link_id}')
        response = midas_api.request("DELETE", f"/db/ELNK/{link_id}")
        if response:
            print(f"弹性连接 {link_id} 删除成功")
            return response
        print(f"弹性连接 {link_id} 删除失败")
        return None

    def _prepare_general_link_data(self, link_id, node_pair, angle, rs, sdr, bshear, dr, bngr_name):
        """准备一般弹性连接数据"""
        return {
            "Assign": {
                str(link_id): {
                    "NODE": node_pair,
                    "LINK": "GEN",
                    "ANGLE": angle,
                    "R_S": rs or [False] * 6,
                    "SDR": sdr or [0] * 6,
                    "bSHEAR": bshear,
                    "DR": dr or [0.5, 0.5],
                    "BNGR_NAME": bngr_name
                }
            }
        }

    def _prepare_rigid_link_data(self, link_id, node_pair, angle, bngr_name):
        """准备刚性连接数据"""
        return {
            "Assign": {
                str(link_id): {
                    "NODE": node_pair,
                    "LINK": "RIGID",
                    "ANGLE": angle,
                    "BNGR_NAME": bngr_name
                }
            }
        }

    def _prepare_nonlinear_link_data(self, link_id, node_pair, link_type, angle, sdr, bngr_name):
        """准备非线性连接数据"""
        return {
            "Assign": {
                str(link_id): {
                    "NODE": node_pair,
                    "LINK": link_type,
                    "ANGLE": angle,
                    "SDR": sdr or [0] * 6,
                    "BNGR_NAME": bngr_name
                }
            }
        }

class LoadProcessor:
    """荷载处理基类"""
    
    def __init__(self, load_type, base_url):
        """
        初始化函数
        
        参数:
        - load_type: str, 荷载类型
        - base_url: str, 基础URL
        """
        self.load_type = load_type
        self.base_url = base_url
        
    def query(self):
        """查询荷载数据"""
        print(f'开始查询{self.load_type}荷载')
        response = midas_api.request("GET", self.base_url, {})
        if response:
            print(f"{self.load_type}荷载查询完成")
            return response
        print(f"{self.load_type}荷载查询失败")
        return None
        
    def add(self, elem_id, data):
        """添加荷载"""
        print(f'开始添加{self.load_type}荷载到单元 {elem_id}')
        response = midas_api.request("POST", self.base_url, data)
        if response:
            print(f"单元 {elem_id} {self.load_type}荷载添加成功")
            return response
        print(f"单元 {elem_id} {self.load_type}荷载添加失败")
        return None
        
    def update(self, elem_id, data):
        """更新荷载"""
        print(f'开始更新单元 {elem_id} 的{self.load_type}荷载')
        response = midas_api.request("PUT", self.base_url, data)
        if response:
            print(f"单元 {elem_id} {self.load_type}荷载更新成功")
            return response
        print(f"单元 {elem_id} {self.load_type}荷载更新失败")
        return None
        
    def delete(self, elem_id):
        """删除单个荷载"""
        print(f'开始删除单元 {elem_id} 的{self.load_type}荷载')
        response = midas_api.request("DELETE", f"{self.base_url}/{elem_id}")
        if response:
            print(f"单元 {elem_id} {self.load_type}荷载删除成功")
            return response
        print(f"单元 {elem_id} {self.load_type}荷载删除失败")
        return None
        
    def delete_all(self):
        """删除所有荷载"""
        print(f'开始删除所有{self.load_type}荷载')
        response = midas_api.request("DELETE", self.base_url)
        if response:
            print(f"所有{self.load_type}荷载删除成功")
            return response
        print(f"删除所有{self.load_type}荷载失败")
        return None


class PrestressLoadsProcessor(LoadProcessor):
    """预应力荷载处理类"""
    
    def __init__(self):
        super().__init__("PRESTRESS", "/db/TDPL")
        self.TENDON_TYPES = {
            'FORCE': 'FORCE',    # 输入预应力力值
            'STRESS': 'STRESS'   # 输入预应力应力值
        }
        self.TENSION_ORDERS = {
            'BEGIN': 'BEGIN',    # 起点张拉
            'END': 'END',        # 终点张拉
            'BOTH': 'BOTH'       # 两端张拉
        }
        self.BEAM_PRESTRESS_DIRS = {
            'Y': 0,  # 局部坐标系y方向
            'Z': 1   # 局部坐标系z方向
        }
        
    def add_tendon_prestress(self, tendon_id, tendon_name, load_case, begin_value, end_value=None,
                            group_name="", prestress_type="STRESS", tension_order="BOTH", 
                            grouting_stage=1):
        """
        添加钢束预应力
        
        参数:
        - tendon_id: int/str, 钢束编号
        - tendon_name: str, 预应力钢束名称
        - load_case: str, 荷载工况名称
        - begin_value: float, 起点预应力值（力或应力）
        - end_value: float, 终点预应力值（力或应力），默认与begin_value相同
        - group_name: str, 荷载组名称（可选，默认为空字符串）
        - prestress_type: str, 预应力类型（'FORCE'或'STRESS'，默认为'STRESS'）
        - tension_order: str, 张拉方式（'BEGIN','END'或'BOTH'，默认为'BOTH'）
        - grouting_stage: int, 注浆工况编号（默认为1）
        
        返回:
        - dict: API响应结果
        """
        if prestress_type not in self.TENDON_TYPES:
            raise ValueError(f"不支持的预应力类型: {prestress_type}")
        if tension_order not in self.TENSION_ORDERS:
            raise ValueError(f"不支持的张拉方式: {tension_order}")
            
        # 如果未指定终点预应力值，则使用起点值
        end_value = end_value if end_value is not None else begin_value
            
        prestress_data = {
            "Assign": {
                str(tendon_id): {
                    "ITEMS": [
                        {
                            "ID": 1,
                            "LCNAME": load_case,
                            "GROUP_NAME": group_name,
                            "TENDON_NAME": tendon_name,
                            "TYPE": prestress_type,
                            "ORDER": tension_order,
                            "BEGIN": begin_value,
                            "END": end_value,
                            "GROUTING": grouting_stage
                        }
                    ]
                }
            }
        }
        
        return self.add(tendon_id, prestress_data)
        
    def update_tendon_prestress(self, tendon_id, **kwargs):
        """
        更新钢束预应力
        
        参数:
        - tendon_id: int/str, 钢束编号
        - kwargs: 可包含以下参数:
            - tendon_name: str, 预应力钢束名称
            - load_case: str, 荷载工况名称
            - begin_value: float, 起点预应力值
            - end_value: float, 终点预应力值
            - group_name: str, 荷载组名称
            - prestress_type: str, 预应力类型
            - tension_order: str, 张拉方式
            - grouting_stage: int, 注浆工况编号
        """
        if 'prestress_type' in kwargs and kwargs['prestress_type'] not in self.TENDON_TYPES:
            raise ValueError(f"不支持的预应力类型: {kwargs['prestress_type']}")
        if 'tension_order' in kwargs and kwargs['tension_order'] not in self.TENSION_ORDERS:
            raise ValueError(f"不支持的张拉方式: {kwargs['tension_order']}")
            
        prestress_data = {
            "Assign": {
                str(tendon_id): {
                    "ITEMS": [
                        {
                            "ID": 1,
                            "LCNAME": kwargs.get("load_case"),
                            "GROUP_NAME": kwargs.get("group_name", ""),
                            "TENDON_NAME": kwargs.get("tendon_name"),
                            "TYPE": kwargs.get("prestress_type"),
                            "ORDER": kwargs.get("tension_order"),
                            "BEGIN": kwargs.get("begin_value"),
                            "END": kwargs.get("end_value"),
                            "GROUTING": kwargs.get("grouting_stage")
                        }
                    ]
                }
            }
        }
        
        # 移除None值的键
        items_dict = prestress_data["Assign"][str(tendon_id)]["ITEMS"][0]
        prestress_data["Assign"][str(tendon_id)]["ITEMS"][0] = {
            k: v for k, v in items_dict.items() if v is not None
        }
        
        return self.update(tendon_id, prestress_data)
        
    def add_beam_prestress(self, elem_id, load_case, tension, distance_i, distance_m, distance_j,
                          group_name="", direction=None):
        """
        添加梁单元预应力
        
        参数:
        - elem_id: int/str, 单元编号
        - load_case: str, 荷载工况名称
        - tension: float, 张拉力大小
        - distance_i: float, i端偏心距
        - distance_m: float, 跨中偏心距
        - distance_j: float, j端偏心距
        - group_name: str, 荷载组名称（可选，默认为空字符串）
        - direction: str, 预应力方向（'Y'或'Z'，默认为'Z'）
        
        返回:
        - dict: API响应结果
        """
        if direction and direction not in self.BEAM_PRESTRESS_DIRS:
            raise ValueError(f"不支持的预应力方向: {direction}。支持的方向: Y, Z")
            
        prestress_data = {
            "Assign": {
                str(elem_id): {
                    "ITEMS": [
                        {
                            "ID": 1,
                            "LCNAME": load_case,
                            "GROUP_NAME": group_name,
                            "DIR": self.BEAM_PRESTRESS_DIRS.get(direction, 1),  # 默认为Z方向(1)
                            "TENSION": tension,
                            "DISTANCE_I": distance_i,
                            "DISTANCE_M": distance_m,
                            "DISTANCE_J": distance_j
                        }
                    ]
                }
            }
        }
        
        return self.add(elem_id, prestress_data)
        
    def update_beam_prestress(self, elem_id, **kwargs):
        """
        更新梁单元预应力
        
        参数:
        - elem_id: int/str, 单元编号
        - kwargs: 可包含以下参数:
            - load_case: str, 荷载工况名称
            - tension: float, 张拉力大小
            - distance_i: float, i端偏心距
            - distance_m: float, 跨中偏心距
            - distance_j: float, j端偏心距
            - group_name: str, 荷载组名称
            - direction: str, 预应力方向（'Y'或'Z'）
        """
        if 'direction' in kwargs:
            if kwargs['direction'] not in self.BEAM_PRESTRESS_DIRS:
                raise ValueError(f"不支持的预应力方向: {kwargs['direction']}")
            kwargs['DIR'] = self.BEAM_PRESTRESS_DIRS[kwargs.pop('direction')]
            
        prestress_data = {
            "Assign": {
                str(elem_id): {
                    "ITEMS": [
                        {
                            "ID": 1,
                            "LCNAME": kwargs.get("load_case"),
                            "GROUP_NAME": kwargs.get("group_name", ""),
                            "DIR": kwargs.get("DIR"),
                            "TENSION": kwargs.get("tension"),
                            "DISTANCE_I": kwargs.get("distance_i"),
                            "DISTANCE_M": kwargs.get("distance_m"),
                            "DISTANCE_J": kwargs.get("distance_j")
                        }
                    ]
                }
            }
        }
        
        # 移除None值的键
        items_dict = prestress_data["Assign"][str(elem_id)]["ITEMS"][0]
        prestress_data["Assign"][str(elem_id)]["ITEMS"][0] = {
            k: v for k, v in items_dict.items() if v is not None
        }
        
        return self.update(elem_id, prestress_data)
    
    def add_initial_tension(self, elem_id, load_case, tension, group_name=""):
        """
        添加初拉力
        
        参数:
        - elem_id: int/str, 单元编号
        - load_case: str, 荷载工况名称
        - tension: float, 初拉力大小
        - group_name: str, 荷载组名称（可选，默认为空字符串）
        
        返回:
        - dict: API响应结果
        """
        tension_data = {
            "Assign": {
                str(elem_id): {
                    "ITEMS": [
                        {
                            "ID": 1,
                            "LCNAME": load_case,
                            "GROUP_NAME": group_name,
                            "TENSION": tension
                        }
                    ]
                }
            }
        }
        
        return self.add(elem_id, tension_data)
    
    def update_initial_tension(self, elem_id, **kwargs):
        """
        更新初拉力
        
        参数:
        - elem_id: int/str, 单元编号
        - kwargs: 可包含以下参数:
            - load_case: str, 荷载工况名称
            - tension: float, 初拉力大小
            - group_name: str, 荷载组名称
        """
        tension_data = {
            "Assign": {
                str(elem_id): {
                    "ITEMS": [
                        {
                            "ID": 1,
                            "LCNAME": kwargs.get("load_case"),
                            "GROUP_NAME": kwargs.get("group_name", ""),
                            "TENSION": kwargs.get("tension")
                        }
                    ]
                }
            }
        }
        
        # 移除None值的键
        items_dict = tension_data["Assign"][str(elem_id)]["ITEMS"][0]
        tension_data["Assign"][str(elem_id)]["ITEMS"][0] = {
            k: v for k, v in items_dict.items() if v is not None
        }
        
        return self.update(elem_id, tension_data)

class StaticLoadsProcessor(LoadProcessor):
    """静力荷载处理类"""
    
    def __init__(self):
        super().__init__("STATIC", "/db/STLD")
        self.load_case_types = {
            'CS': '施工阶段荷载',
            'L': '活荷载',
            'PS': '预应力',
            'W': '风荷载',
            'CR': '徐变',
            'SH': '收缩',
            'T': '温度荷载',
            'TPG': '温度梯度',
            'D': '恒荷载'
        }
        
    def query_load_cases(self):
        """查询所有静力荷载工况"""
        print('开始查询静力荷载工况')
        response = midas_api.request("GET", self.base_url, {})
        if response:
            print("静力荷载工况查询完成")
            return response
        print("静力荷载工况查询失败")
        return None
        
    def add_load_case(self, case_id, name, case_type, description=""):
        """
        添加静力荷载工况
        
        参数:
        - case_id: int/str, 工况编号
        - name: str, 工况名称
        - case_type: str, 工况类型（'CS','L','PS','W','CR','SH','T','TPG','D'）
        - description: str, 工况描述（可选）
        
        返回:
        - dict: API响应结果
        """
        if case_type not in self.load_case_types:
            raise ValueError(f"不支持的工况类型: {case_type}。支持的类型: {', '.join(self.load_case_types.keys())}")
            
        case_data = {
            "Assign": {
                str(case_id): {
                    "NAME": name,
                    "TYPE": case_type,
                    "DESC": description or self.load_case_types[case_type]
                }
            }
        }
        
        print(f'开始添加静力荷载工况 {name}')
        return self.add(case_id, case_data)
        
    def update_load_case(self, case_id, **kwargs):
        """
        更新静力荷载工况
        
        参数:
        - case_id: int/str, 工况编号
        - kwargs: 可包含以下参数:
            - name: str, 工况名称
            - case_type: str, 工况类型
            - description: str, 工况描述
            
        返回:
        - dict: API响应结果
        """
        if 'case_type' in kwargs and kwargs['case_type'] not in self.load_case_types:
            raise ValueError(f"不支持的工况类型: {kwargs['case_type']}")
            
        case_data = {
            "Assign": {
                str(case_id): {
                    "NAME": kwargs.get('name'),
                    "TYPE": kwargs.get('case_type'),
                    "DESC": kwargs.get('description', '')
                }
            }
        }
        
        # 移除None值的键
        case_data["Assign"][str(case_id)] = {
            k: v for k, v in case_data["Assign"][str(case_id)].items() 
            if v is not None
        }
        
        print(f'开始更新静力荷载工况 {case_id}')
        return self.update(case_id, case_data)
        
    def delete_load_case(self, case_id):
        """
        删除静力荷载工况
        
        参数:
        - case_id: int/str, 工况编号
        
        返回:
        - dict: API响应结果
        """
        print(f'开始删除静力荷载工况 {case_id}')
        return self.delete(case_id)
        
    def delete_all_load_cases(self):
        """
        删除所有静力荷载工况
        
        返回:
        - dict: API响应结果
        """
        print('开始删除所有静力荷载工况')
        return self.delete_all()
        
    def query_self_weight(self):
        """
        查询自重荷载数据
        
        返回:
        - dict: API响应结果，包含所有自重荷载信息
        """
        print('开始查询自重荷载')
        return self.query()
        
    def add_self_weight(self, case_id, load_case="自重", group_name="", fv=None):
        """
        添加自重荷载
        
        参数:
        - case_id: int/str, 自重荷载编号
        - load_case: str, 荷载工况名称，默认为"自重"
        - group_name: str, 荷载组名称，默认为空字符串
        - fv: list, 自重方向向量[x, y, z]，默认为[0, 0, -1]
        
        返回:
        - dict: API响应结果
        """
        if fv is None:
            fv = [0, 0, -1]
            
        if len(fv) != 3:
            raise ValueError("自重方向向量必须包含3个分量[x, y, z]")
            
        weight_data = {
            "Assign": {
                str(case_id): {
                    "LCNAME": load_case,
                    "GROUP_NAME": group_name,
                    "FV": fv
                }
            }
        }
        
        print(f'开始添加自重荷载，工况: {load_case}')
        return self.add(case_id, weight_data)
        
    def update_self_weight(self, case_id, **kwargs):
        """
        更新自重荷载
        
        参数:
        - case_id: int/str, 自重荷载编号
        - kwargs: 可包含以下参数:
            - load_case: str, 荷载工况名称
            - group_name: str, 荷载组名称
            - fv: list, 自重方向向量[x, y, z]
            
        返回:
        - dict: API响应结果
        """
        weight_data = {
            "Assign": {
                str(case_id): {
                    "LCNAME": kwargs.get("load_case"),
                    "GROUP_NAME": kwargs.get("group_name"),
                    "FV": kwargs.get("fv")
                }
            }
        }
        
        # 移除None值的键
        weight_data["Assign"][str(case_id)] = {
            k: v for k, v in weight_data["Assign"][str(case_id)].items() 
            if v is not None
        }
        
        print(f'开始更新自重荷载 {case_id}')
        return self.update(case_id, weight_data)
        
    def delete_self_weight(self, case_id):
        """
        删除指定的自重荷载
        
        参数:
        - case_id: int/str, 自重荷载编号
        
        返回:
        - dict: API响应结果
        """
        print(f'开始删除自重荷载 {case_id}')
        return self.delete(case_id)
        
    def delete_all_self_weights(self):
        """
        删除所有自重荷载
        
        返回:
        - dict: API响应结果
        """
        print('开始删除所有自重荷载')
        return self.delete_all()

    def query_nodal_loads(self):
        """
        查询节点荷载数据
        
        返回:
        - dict: API响应结果，包含所有节点荷载信息
        """
        print('开始查询节点荷载')
        return self.query()
    
    def add_nodal_load(self, node_id, load_case, group_name="", fx=0, fy=0, fz=0, mx=0, my=0, mz=0):
        """
        添加节点荷载
        
        参数:
        - node_id: int/str, 节点编号
        - load_case: str, 荷载工况名称
        - group_name: str, 荷载组名称，默认为空字符串
        - fx: float, X方向集中力，默认为0
        - fy: float, Y方向集中力，默认为0
        - fz: float, Z方向集中力，默认为0
        - mx: float, X方向集中力矩，默认为0
        - my: float, Y方向集中力矩，默认为0
        - mz: float, Z方向集中力矩，默认为0
        
        返回:
        - dict: API响应结果
        """
        load_data = {
            "Assign": {
                str(node_id): {
                    "ITEMS": [
                        {
                            "ID": 1,
                            "LCNAME": load_case,
                            "GROUP_NAME": group_name,
                            "FX": fx,
                            "FY": fy,
                            "FZ": fz,
                            "MX": mx,
                            "MY": my,
                            "MZ": mz
                        }
                    ]
                }
            }
        }
        
        print(f'开始添加节点 {node_id} 的荷载')
        return self.add(node_id, load_data)
    
    def update_nodal_load(self, node_id, **kwargs):
        """
        更新节点荷载
        
        参数:
        - node_id: int/str, 节点编号
        - kwargs: 可包含以下参数:
            - load_case: str, 荷载工况名称
            - group_name: str, 荷载组名称
            - fx: float, X方向集中力
            - fy: float, Y方向集中力
            - fz: float, Z方向集中力
            - mx: float, X方向集中力矩
            - my: float, Y方向集中力矩
            - mz: float, Z方向集中力矩
            
        返回:
        - dict: API响应结果
        """
        load_data = {
            "Assign": {
                str(node_id): {
                    "ITEMS": [
                        {
                            "ID": 1,
                            "LCNAME": kwargs.get("load_case"),
                            "GROUP_NAME": kwargs.get("group_name", ""),
                            "FX": kwargs.get("fx", 0),
                            "FY": kwargs.get("fy", 0),
                            "FZ": kwargs.get("fz", 0),
                            "MX": kwargs.get("mx", 0),
                            "MY": kwargs.get("my", 0),
                            "MZ": kwargs.get("mz", 0)
                        }
                    ]
                }
            }
        }
        
        print(f'开始更新节点 {node_id} 的荷载')
        return self.update(node_id, load_data)
    
    def delete_nodal_load(self, node_id):
        """
        删除指定节点的荷载
        
        参数:
        - node_id: int/str, 节点编号
        
        返回:
        - dict: API响应结果
        """
        print(f'开始删除节点 {node_id} 的荷载')
        return self.delete(node_id)
    
    def delete_all_nodal_loads(self):
        """
        删除所有节点荷载
        
        返回:
        - dict: API响应结果
        """
        print('开始删除所有节点荷载')
        return self.delete_all()

class TemperatureLoadsProcessor(LoadProcessor):
    """温度荷载处理类"""
    
    def __init__(self):
        super().__init__("TEMPERATURE", "/db/ETMP")
        self.ELEMENT_TYPES = {
            'BEAM': 1,  # 梁单元
            'PLATE': 2  # 板单元
        }
        
    def add_uniform_temp(self):
        """添加均匀温度荷载"""
        pass
        
    def add_gradient_temp(self):
        """添加温度梯度荷载"""
        pass
        
    def query_element_temps(self):
        """
        查询单元温度数据
        
        返回:
        - dict: API响应结果，包含所有单元温度信息
        """
        print('开始查询单元温度')
        return self.query()
        
    def add_element_temp(self, elem_id, temps_data):
        """
        添加单元温度
        
        参数:
        - elem_id: int/str, 单元编号
        - temps_data: list of dict, 温度数据列表，每个字典包含:
            - load_case: str, 荷载工况名称
            - group_name: str, 荷载组名称（可选，默认为空字符串）
            - temp: float, 温度值
        
        示例:
        temps_data = [
            {"load_case": "Temp(+)", "temp": 35},
            {"load_case": "Temp(-)", "temp": -20}
        ]
        
        返回:
        - dict: API响应结果
        """
        items = []
        for i, data in enumerate(temps_data, 1):
            items.append({
                "ID": i,
                "LCNAME": data["load_case"],
                "GROUP_NAME": data.get("group_name", ""),
                "TEMP": data["temp"]
            })
            
        temp_data = {
            "Assign": {
                str(elem_id): {
                    "ITEMS": items
                }
            }
        }
        
        print(f'开始添加单元 {elem_id} 的温度荷载')
        return self.add(elem_id, temp_data)
        
    def update_element_temp(self, elem_id, temps_data):
        """
        更新单元温度
        
        参数:
        - elem_id: int/str, 单元编号
        - temps_data: list of dict, 温度数据列表，每个字典包含:
            - load_case: str, 荷载工况名称
            - group_name: str, 荷载组名称（可选，默认为空字符串）
            - temp: float, 温度值
            
        返回:
        - dict: API响应结果
        """
        items = []
        for i, data in enumerate(temps_data, 1):
            items.append({
                "ID": i,
                "LCNAME": data["load_case"],
                "GROUP_NAME": data.get("group_name", ""),
                "TEMP": data["temp"]
            })
            
        temp_data = {
            "Assign": {
                str(elem_id): {
                    "ITEMS": items
                }
            }
        }
        
        print(f'开始更新单元 {elem_id} 的温度荷载')
        return self.update(elem_id, temp_data)
        
    def delete_element_temp(self, elem_id):
        """
        删除指定单元的温度荷载
        
        参数:
        - elem_id: int/str, 单元编号
        
        返回:
        - dict: API响应结果
        """
        print(f'开始删除单元 {elem_id} 的温度荷载')
        return self.delete(elem_id)
        
    def delete_all_element_temps(self):
        """
        删除所有单元温度荷载
        
        返回:
        - dict: API响应结果
        """
        print('开始删除所有单元温度荷载')
        return self.delete_all()

    def query_gradient_temps(self):
        """
        查询温度梯度荷载数据
        
        返回:
        - dict: API响应结果，包含所有温度梯度荷载信息
        """
        print('开始查询温度梯度荷载')
        return self.query()
        
    def add_beam_gradient_temp(self, elem_id, temps_data):
        """
        添加梁单元温度梯度荷载
        
        参数:
        - elem_id: int/str, 单元编号
        - temps_data: list of dict, 温度数据列表，每个字典包含:
            - load_case: str, 荷载工况名称
            - group_name: str, 荷载组名称（可选，默认为空字符串）
            - tz: float, Z方向温度梯度值
            - ty: float, Y方向温度梯度值
            - use_hz: bool, 是否使用默认高度（可选，默认True）
            - hz: float, Z方向高度（当use_hz为False时必需）
            - use_hy: bool, 是否使用默认高度（可选，默认True）
            - hy: float, Y方向高度（当use_hy为False时必需）
        
        示例:
        temps_data = [
            {
                "load_case": "Temp(+)",
                "tz": 10,
                "ty": -10
            },
            {
                "load_case": "Temp(-)",
                "tz": 10,
                "ty": -10,
                "use_hz": False,
                "hz": 1.2,
                "use_hy": False,
                "hy": 0.5
            }
        ]
        """
        items = []
        for i, data in enumerate(temps_data, 1):
            item = {
                "ID": i,
                "LCNAME": data["load_case"],
                "GROUP_NAME": data.get("group_name", ""),
                "TYPE": self.ELEMENT_TYPES['BEAM'],
                "TZ": data["tz"],
                "TY": data["ty"],
                "USE_HZ": data.get("use_hz", True),
                "USE_HY": data.get("use_hy", True)
            }
            
            # 添加可选的高度参数
            if not item["USE_HZ"] and "hz" in data:
                item["HZ"] = data["hz"]
            if not item["USE_HY"] and "hy" in data:
                item["HY"] = data["hy"]
                
            items.append(item)
            
        temp_data = {
            "Assign": {
                str(elem_id): {
                    "ITEMS": items
                }
            }
        }
        
        print(f'开始添加梁单元 {elem_id} 的温度梯度荷载')
        return self.add(elem_id, temp_data)
        
    def add_plate_gradient_temp(self, elem_id, temps_data):
        """
        添加板单元温度梯度荷载
        
        参数:
        - elem_id: int/str, 单元编号
        - temps_data: list of dict, 温度数据列表，每个字典包含:
            - load_case: str, 荷载工况名称
            - group_name: str, 荷载组名称（可选，默认为空字符串）
            - tz: float, Z方向温度梯度值
            - use_hz: bool, 是否使用默认高度（可选，默认True）
            - hz: float, Z方向高度（当use_hz为False时必需）
            
        示例:
        temps_data = [
            {
                "load_case": "Temp(+)",
                "tz": 10
            },
            {
                "load_case": "Temp(-)",
                "tz": 10,
                "use_hz": False,
                "hz": 0.2
            }
        ]
        """
        items = []
        for i, data in enumerate(temps_data, 1):
            item = {
                "ID": i,
                "LCNAME": data["load_case"],
                "GROUP_NAME": data.get("group_name", ""),
                "TYPE": self.ELEMENT_TYPES['PLATE'],
                "TZ": data["tz"],
                "USE_HZ": data.get("use_hz", True)
            }
            
            # 添加可选的高度参数
            if not item["USE_HZ"] and "hz" in data:
                item["HZ"] = data["hz"]
                
            items.append(item)
            
        temp_data = {
            "Assign": {
                str(elem_id): {
                    "ITEMS": items
                }
            }
        }
        
        print(f'开始添加板单元 {elem_id} 的温度梯度荷载')
        return self.add(elem_id, temp_data)
        
    def update_gradient_temp(self, elem_id, temps_data):
        """
        更新温度梯度荷载
        
        参数与add_beam_gradient_temp或add_plate_gradient_temp相同
        """
        # 检查第一个数据项确定单元类型
        if "ty" in temps_data[0]:  # 梁单元
            return self.add_beam_gradient_temp(elem_id, temps_data)
        else:  # 板单元
            return self.add_plate_gradient_temp(elem_id, temps_data)
        
    def delete_gradient_temp(self, elem_id):
        """
        删除指定单元的温度梯度荷载
        
        参数:
        - elem_id: int/str, 单元编号
        """
        print(f'开始删除单元 {elem_id} 的温度梯度荷载')
        return self.delete(elem_id)
        
    def delete_all_gradient_temps(self):
        """删除所有温度梯度荷载"""
        print('开始删除所有温度梯度荷载')
        return self.delete_all()

    def query_system_temps(self):
        """
        查询系统温度数据
        
        返回:
        - dict: API响应结果，包含所有系统温度信息
        """
        print('开始查询系统温度')
        return self.query()
    
    def add_system_temp(self, temp_id, temperature, load_case, group_name=""):
        """
        添加系统温度
        
        参数:
        - temp_id: int/str, 温度编号
        - temperature: float, 温度值
        - load_case: str, 荷载工况名称
        - group_name: str, 荷载组名称（可选，默认为空字符串）
        
        返回:
        - dict: API响应结果
        """
        temp_data = {
            "Assign": {
                str(temp_id): {
                    "TEMPER": temperature,
                    "LCNAME": load_case,
                    "GROUP_NAME": group_name
                }
            }
        }
        
        print(f'开始添加系统温度 {temp_id}')
        return self.add(temp_id, temp_data)
    
    def update_system_temp(self, temp_id, **kwargs):
        """
        更新系统温度
        
        参数:
        - temp_id: int/str, 温度编号
        - kwargs: 可包含以下参数:
            - temperature: float, 温度值
            - load_case: str, 荷载工况名称
            - group_name: str, 荷载组名称
            
        返回:
        - dict: API响应结果
        """
        temp_data = {
            "Assign": {
                str(temp_id): {
                    "TEMPER": kwargs.get("temperature"),
                    "LCNAME": kwargs.get("load_case"),
                    "GROUP_NAME": kwargs.get("group_name", "")
                }
            }
        }
        
        # 移除None值的键
        temp_data["Assign"][str(temp_id)] = {
            k: v for k, v in temp_data["Assign"][str(temp_id)].items() 
            if v is not None
        }
        
        print(f'开始更新系统温度 {temp_id}')
        return self.update(temp_id, temp_data)
    
    def delete_system_temp(self, temp_id):
        """
        删除指定的系统温度
        
        参数:
        - temp_id: int/str, 温度编号
        
        返回:
        - dict: API响应结果
        """
        print(f'开始删除系统温度 {temp_id}')
        return self.delete(temp_id)
    
    def delete_all_system_temps(self):
        """
        删除所有系统温度
        
        返回:
        - dict: API响应结果
        """
        print('开始删除所有系统温度')
        return self.delete_all()

class ConstructionStageProcessor(LoadProcessor):
    """施工阶段处理类"""

    def __init__(self):
        super().__init__("CONSTRUCTION_STAGE", "/db/STAG")

    def query_construction_stages(self):
        """
        查询当前施工阶段数量
        
        返回:
        - dict: API响应结果，包含所有施工阶段信息
        """
        print('开始查询施工阶段')
        response = midas_api.request("GET", self.base_url, {})
        if response:
            print("施工阶段查询完成")
            return response
        print("施工阶段查询失败")
        return None
