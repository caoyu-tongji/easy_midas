Structural Analysis Package
==========================

项目简介
--------
Structural Analysis Package 是一个基于 Python 的结构分析后处理工具包，主要用于提取和可视化 MIDAS 结构分析结果。该工具包支持多种单元类型的内力、应力分析以及节点位移分析，并可处理 General 分析和施工阶段分析结果。

主要功能
--------

基础操作功能
1. MIDAS Civil操作
   - 打开软件
   - 打开模型文件
   - 运行分析
   - 保存文件

前处理功能
1. 单位系统设置
   - 力单位设置
   - 长度单位设置

2. 节点处理
   - 节点创建
   - 节点查询
   - 节点更新
   - 节点删除（单个/全部）

3. 单元处理
   - 梁单元
   - 桁架单元
   - 索单元
   - 支持材料和截面属性设置

4. 边界条件
   - 支承约束
   - 弹性支撑（线性/非线性）
   - 刚性连接
   - 弹性连接

5. 施工阶段处理
   - 施工阶段查询
   - 施工阶段信息获取

后处理功能
1. 结果提取
   支持以下类型的结果提取：
   - 梁单元结果
     * 内力分析（轴力、剪力、弯矩等）
     * 应力分析（含七自由度）
   - 桁架单元结果
     * 内力分析
     * 应力分析
   - 索单元结果
     * 内力分析
     * 索效应分析
     * 几何信息提取
   - 节点位移结果
     * 位移分量（DX, DY, DZ）
     * 转角分量（RX, RY, RZ）

2. 数据处理
   - 支持多种单元/节点选择方式
     * 指定具体编号：[1, 2, 3]
     * 指定编号范围："1 to 10"
     * 指定结构组名称："SG1"
   - 灵活的单位系统设置
     * 力单位：N, kN, MN
     * 长度单位：mm, m
   - 可调整的数据格式化选项
     * 数据格式：Fixed, Scientific
     * 小数位数自定义

3. 可视化功能
   - 内力图
     * 轴力图
     * 剪力图
     * 弯矩图
   - 应力图
   - 位移图
   - 支持施工阶段分析结果的动态展示

使用指南
--------

1. 安装
   pip install structural-analysis

2. 基本用法
   from structural_analysis.post_processor import create_processor

   # 创建处理器
   processor = create_processor("beam_force")

   # 提取结果
   results = processor.extract_general(
       elems=[1, 2, 3],
       load_case="COMB1"
   )

   # 处理数据
   df = processor.process_general_results(results)

   # 绘制结果
   processor.plot_results(df, component="Moment-y")

3. 结果类型
   类型标识            说明              支持的分析类型
   ------------------------------------------------
   beam_force        梁单元内力        General/Construction
   beam_stress       梁单元应力        General/Construction
   beam_stress_7dof  七自由度梁单元应力  General/Construction
   truss_force       桁架单元内力       General/Construction
   truss_stress      桁架单元应力       General/Construction
   cable_force       索单元内力         General/Construction
   cable_efficiency  索效应            General/Construction
   cable_config      索信息            General/Construction
   displacement      节点位移          General/Construction

4. 参数设置
   kwargs = {
       # 单位设置
       "force_unit": "N",     # 力单位
       "dist_unit": "mm",     # 距离单位
       
       # 输出格式
       "format_style": "Fixed",  # 数据格式
       "decimal_places": 6       # 小数位数
   }

示例
----

基础操作示例
1. 软件操作
   # 打开软件并加载模型
   from structural_analysis.operations import MidasOperations
   
   # 打开MIDAS Civil并加载模型
   civil_path = "C:/Program Files/MIDAS/Civil/Civil.exe"
   model_path = "C:/Projects/bridge.mcb"
   MidasOperations.open_file(civil_path, model_path)
   
   # 运行分析
   MidasOperations.analyze()
   
   # 保存文件
   MidasOperations.save_file("C:/Projects/bridge_new.mcb")

前处理示例
1. 单位设置
   from structural_analysis.pre_processor import PreProcessor
   
   # 设置单位系统
   PreProcessor.set_units(force_unit="kN", dist_unit="m")

2. 材料定义
   # 定义钢材
   PreProcessor.define_material(
       material_id=1,
       TYPE="STEEL",
       NAME="Q345",
       ELAST=2.06e8,
       POISN=0.3,
       DEN=7849.0474
   )

3. 节点处理
   from structural_analysis.pre_processor import NodeProcessor
   
   node_proc = NodeProcessor()
   
   # 创建节点
   node_data = {
       "Assign": {
           "1": {"X": 0.0, "Y": 0.0, "Z": 0.0},
           "2": {"X": 5.0, "Y": 0.0, "Z": 0.0}
       }
   }
   node_proc.create(node_data)
   
   # 查询节点
   nodes = node_proc.query()

4. 单元处理
   from structural_analysis.pre_processor import BeamElement, TrussElement, CableElement
   
   # 创建梁单元
   beam = BeamElement()
   beam.create(
       element_id=1,
       matl=1,
       sect=1,
       nodes=[1, 2],
       angle=0
   )
   
   # 创建桁架单元
   truss = TrussElement()
   truss.create(
       element_id=2,
       matl=1,
       sect=2,
       nodes=[2, 3]
   )
   
   # 创建索单元
   cable = CableElement()
   cable.create(
       element_id=3,
       matl=1,
       sect=3,
       nodes=[3, 4],
       cable_type=3,
       non_len=1.0
   )

5. 边界条件
   from structural_analysis.pre_processor import BoundaryConditionProcessor
   
   bc_proc = BoundaryConditionProcessor()
   
   # 添加支承约束
   bc_proc.add_support(
       node_id=1,
       dx=True, dy=True, dz=True,
       rx=True, ry=True, rz=True
   )
   
   # 添加弹性支撑
   bc_proc.add_elastic_support(
       node_id=2,
       kx=1000, ky=1000, kz=1000
   )

6. 施工阶段处理
   from structural_analysis import ConstructionStageProcessor
   
   # 创建施工阶段处理器
   stages_proc = ConstructionStageProcessor()
   
   # 查询施工阶段
   stages = stages_proc.query_construction_stages()
   print("当前施工阶段:", stages)
   
   # 通过MidasCivil接口访问
   midas = MidasCivil()
   stages = midas.construction.query_construction_stages()

后处理示例
1. 梁单元内力分析
   # 创建梁单元内力处理器
   beam_processor = create_processor("beam_force")
   
   # 提取内力
   results = beam_processor.extract_general(
       elems=[101, 102, 103],
       load_case="COMB1",
       force_unit="kN",
       dist_unit="m"
   )
   
   # 处理并绘图
   df = beam_processor.process_general_results(results)
   beam_processor.plot_results(df, component="Moment-y")

2. 桁架单元分析
   # 创建桁架单元内力处理器
   truss_processor = create_processor("truss_force")
   
   # 提取内力
   results = truss_processor.extract_general(
       elems="1 to 10",
       load_case="COMB1"
   )
   
   # 处理并绘图
   df = truss_processor.process_general_results(results)
   truss_processor.plot_results(df, component="Axial")

3. 索单元分析
   # 创建索单元内力处理器
   cable_processor = create_processor("cable_force")
   
   # 提取施工阶段结果
   results = cable_processor.extract_construction(
       elems="1 to 10",
       load_case="合计(CS)",
       stages=["CS1:001", "CS2:001"]
   )
   
   # 处理并绘图
   df_list = cable_processor.process_construction_results(results)
   cable_processor.plot_results(df_list, component="Tension")

4. 节点位移分析
   # 创建节点位移处理器
   disp_processor = create_processor("displacement")
   
   # 提取位移
   results = disp_processor.extract_general(
       nodes=[1, 2, 3],
       load_case="COMB1"
   )
   
   # 处理并绘图
   df = disp_processor.process_general_results(results)
   disp_processor.plot_results(df, component="DZ")

注意事项
--------

1. 单元/节点选择
   - 确保提供的编号在模型中存在
   - 注意编号范围的合理性
   - 确认结构组名称的正确性

2. 单位系统
   - 保持输入输出单位的一致性
   - 注意不同类型结果的默认单位
   - 单位转换在数据提取时进行

3. 结果处理
   - 选择合适的结果分量进行绘图
   - 注意施工阶段结果的特殊处理方式
   - 数据格式化参数的合理设置

依赖项
------
- Python >= 3.7
- pandas
- numpy
- matplotlib
- requests

版本历史
--------
v1.0.0 (2024-01)
- 初始版本发布
- 支持基本的结果提取和可视化功能

贡献指南
--------
1. Fork 该仓库
2. 创建新的功能分支
3. 提交更改
4. 创建 Pull Request

许可证
------
MIT License

技术支持
--------
- 文档：https://structural-analysis.readthedocs.io/
- 问题反馈：https://github.com/yourusername/structural-analysis/issues
- 邮箱：example@example.com 