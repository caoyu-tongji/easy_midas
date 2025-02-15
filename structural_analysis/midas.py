"""主接口模块，提供MidasCivil类作为统一入口"""

from .operations import MidasOperations
from .pre_processor import (
    PreProcessor,
    NodeProcessor,
    BeamElement,
    TrussElement,
    CableElement,
    SupportProcessor,
    PointSpringProcessor,
    RigidLinkProcessor,
    ElasticLinkProcessor,
    LoadProcessor,
    StaticLoadsProcessor,
    TemperatureLoadsProcessor,
    PrestressLoadsProcessor,
    ConstructionStageProcessor
)
from .post_processor import create_processor

class MidasCivil:
    """MIDAS Civil API的主接口类"""
    
    def __init__(self):
        """初始化MIDAS Civil接口"""
        self.operations = MidasOperations()
        self.pre = PreProcessor()
        self.post = PostProcessorFactory()
        
        # 添加预处理器
        self.pre.node = NodeProcessor()
        self.pre.beam = BeamElement()
        self.pre.truss = TrussElement()
        self.pre.cable = CableElement()
        self.pre.support = SupportProcessor()
        self.pre.spring = PointSpringProcessor()
        self.pre.rigid_link = RigidLinkProcessor()
        self.pre.elastic_link = ElasticLinkProcessor()
        
        # 添加荷载处理器
        self.pre.static_loads = StaticLoadsProcessor()
        self.pre.temperature_loads = TemperatureLoadsProcessor()
        self.pre.prestress_loads = PrestressLoadsProcessor()
        self.construction = ConstructionStageProcessor()

class PostProcessorFactory:
    """后处理器工厂类"""
    
    def create_processor(self, result_type):
        """创建结果处理器"""
        from .post_processor import create_processor
        return create_processor(result_type) 