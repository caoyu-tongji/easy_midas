"""
梁单元分析示例，展示如何使用结构化的API进行:
- 模型打开和基本设置
- 材料定义
- 分析计算
- 结果提取和可视化
"""

from structural_analysis import MidasCivil

def run_beam_analysis():
    # 创建MIDAS Civil实例
    midas = MidasCivil()
    
    # 定义文件路径
    civil_path = "D:/MIDAS CIVIL/CVLw.exe"
    file_path = "D:/caoyu/硕士毕业课题————施工阶段模型修正/单梁二次开发模型/梁单元案例_20241030_154958_859567.mcb"
    
    # 1. 打开文件
    #midas.operations.open_file(civil_path, file_path)
    '''
    # 2. 设置单位
    midas.pre.set_units(
        force_unit="KN",  # KN, N, KGF, TONF, LBF, KIPS
        dist_unit="M"     # M, CM, MM, IN, FT
    )
    
    # 3. 定义材料属性
    midas.pre.define_material(
        material_id=1,
        TYPE="USER",
        NAME="C50",
        bMASS_DENS=True,
        ELAST=3.45e7,
        POISN=0.2,
        THERMAL=1e-5,
        DEN=25,
        MASS=2.549
    )
    '''
    '''
    # 4.1 添加和管理支撑约束条件
    print("\n=== 开始边界条件操作 ===")
    support = midas.pre.support
    
    # 查询当前支撑条件
    print("\n- 查询当前支撑条件:")
    current_supports = support.query_supports()
    print(current_supports)
    
    # 添加4号和5号节点的支撑约束
    print("\n- 添加节点支撑:")
    support.add_support(4, dx=1, dy=1, dz=1)  # 约束条件1110000
    support.add_support(5, dx=1, dy=1, dz=1)  # 约束条件1110000
    
    # 更新5号节点的支撑约束
    print("\n- 更新节点支撑:")
    support.update_support(5, dx=0, dy=1, dz=1)  # 约束条件改为0110000
    
    # 应用支撑设置
    support.apply_supports()
    
    # 查询更新后的支撑条件
    print("\n- 查询更新后的支撑条件:")
    updated_supports = support.query_supports()
    print(updated_supports)
    
    # 删除4号和5号节点的支撑
    print("\n- 删除节点支撑:")
    support.delete_support(4)
    support.delete_support(5)
    
    # 应用更改
    support.apply_supports()
    
    # 查询最终的支撑条件
    print("\n- 查询最终支撑条件:")
    final_supports = support.query_supports()
    print(final_supports)
    
    print("=== 边界条件操作完成 ===\n")
    '''
    '''
    # 4.2 添加和管理弹性支撑
    print("\n=== 开始弹性支撑操作 ===")
    spring = midas.pre.spring
    
    # 查询当前弹性支撑条件
    print("\n- 查询当前弹性支撑条件:")
    current_springs = spring.query()
    print(current_springs)
    
    # 添加线性弹性支撑到节点5
    print("\n- 添加线性弹性支撑到节点5:")
    spring.add_linear_spring(
        node_id=5,
        damping=False,  # 不开启阻尼
        F_S=[False, False, False, True, True, True],  # 后3个约束固定
        SDR=[1000, 1200, 1400, 0, 0, 0]  # 前3个方向的刚度
    )
    
    # 添加仅受压支座到节点6
    print("\n- 添加仅受压支座到节点6:")
    spring.add_nonlinear_spring(
        node_id=6,
        spring_type="COMP",  # 仅受压
        direction=4,  # Dz(+)方向
        stiffness=200
    )
    
    # 添加仅受拉支座到节点7
    print("\n- 添加仅受拉支座到节点7:")
    spring.add_nonlinear_spring(
        node_id=7,
        spring_type="TENS",  # 仅受拉
        direction=5,  # Dz(-)方向
        stiffness=300
    )
    
    # 查询添加后的弹性支撑条件
    print("\n- 查询更新后的弹性支撑条件:")
    updated_springs = spring.query()
    print(updated_springs)
    
    # 删除节点5的弹性支撑
    print("\n- 删除节点5的弹性支撑:")
    spring.delete_single(5)
    
    # 查询删除单个节点后的弹性支撑条件
    print("\n- 查询删除节点5后的弹性支撑条件:")
    after_delete_springs = spring.query()
    print(after_delete_springs)

    # 删除所有弹性支撑
    print("\n- 删除所有弹性支撑:")
    spring.delete_all()

    # 查询最终的弹性支撑条件
    print("\n- 查询最终弹性支撑条件:")
    final_springs = spring.query()
    print(final_springs)
    
    print("=== 弹性支撑操作完成 ===\n")
    '''
    
    # 4.3 添加和管理刚性连接
    #print("\n=== 开始刚性连接操作 ===")
    #rigid_link = midas.pre.rigid_link
    '''
    # 查询当前刚性连接条件
    print("\n- 查询当前刚性连接条件:")
    current_links = rigid_link.query()
    print(current_links)
    
    # 添加刚性连接 - 主节点1与从节点2,3,4,5之间建立连接
    # 约束DX,DY,RZ方向（110001）
    print("\n- 添加刚性连接:")
    rigid_link.add_rigid_link(
        node_id=1,
        dof=110001,  # DX,DY方向平动刚性，RZ方向转动刚性
        s_node=[2, 3, 4, 5],  # 从节点列表
        group_name=""
    )
    
    # 查询添加后的刚性连接
    print("\n- 查询添加后的刚性连接条件:")
    updated_links = rigid_link.query()
    print(updated_links)
    
    # 更新刚性连接 - 修改主节点1的连接属性
    print("\n- 更新刚性连接:")
    rigid_link.update_rigid_link(
        node_id=1,
        dof=111000,  # 修改为三个平动方向刚性
        s_node=[6, 7, 8, 9],  # 更新从节点列表
        group_name=""
    )
    
    # 查询更新后的刚性连接
    print("\n- 查询更新后的刚性连接条件:")
    after_update_links = rigid_link.query()
    print(after_update_links)

    # 删除节点1的刚性连接
    print("\n- 删除节点1的刚性连接:")
    rigid_link.delete_single(1)
    
    # 查询删除后的刚性连接
    print("\n- 查询删除单个节点后的刚性连接条件:")
    after_delete_links = rigid_link.query()
    print(after_delete_links)
    
    # 删除所有刚性连接
    print("\n- 删除所有刚性连接:")
    rigid_link.delete_all()
    
    # 查询最终的刚性连接条件
    print("\n- 查询最终刚性连接条件:")
    final_links = rigid_link.query()
    print(final_links)
    
    print("=== 刚性连接操作完成 ===\n")
    '''
    # 4. 运行分析
    #midas.operations.analyze()

    '''
    # 5. 结果提取和可视化
    # 5.1 创建结果处理器
    displacement = midas.post.create_processor("displacement")
    beam_force = midas.post.create_processor("beam_force")
    beam_stress = midas.post.create_processor("beam_stress")
    
    # 5.2 General分析结果处理
    # 位移结果
    disp_results = displacement.extract_general(
        nodes="1 to 32",
        load_case="comb1(CB)",
        force_unit="N",
        dist_unit="mm",
        format_style="Scientific",
        decimal_places=3
    )
    df_disp = displacement.process_general_results(disp_results)
    displacement.plot_results(df_disp, component="DZ")
    
    # 内力结果
    force_results = beam_force.extract_general(
        elems="1 to 31",
        load_case="comb1(CB)",
        force_unit="N",
        dist_unit="mm",
        format_style="Fixed",
        decimal_places=6
    )
    df_force = beam_force.process_general_results(force_results)
    beam_force.plot_results(df_force, component="Moment-y")
    
    # 应力结果
    stress_results = beam_stress.extract_general(
        elems="1 to 31",
        load_case="comb1(CB)",
        force_unit="N",
        dist_unit="mm",
        format_style="Fixed",
        decimal_places=6
    )
    df_stress = beam_stress.process_general_results(stress_results)
    beam_stress.plot_results(df_stress, component="Cb(min/max)")
    
    # 5.3 施工阶段结果处理
    # 位移结果
    cs_disp_results = displacement.extract_construction(
        nodes="1 to 32",
        load_case="合计(CS)",
        force_unit="N",
        dist_unit="mm",
        format_style="Scientific",
        decimal_places=6,
        stages=["CS1:002(最后)", "CS2:002(最后)"],
        disp_opt="Accumulative"
    )
    df_cs_disp = displacement.process_construction_results(cs_disp_results)
    displacement.plot_results(df_cs_disp, component="DZ")
    
    # 内力结果
    cs_force_results = beam_force.extract_construction(
        elems="1 to 31",
        load_case="合计(CS)",
        force_unit="N",
        dist_unit="mm",
        format_style="Scientific",
        decimal_places=6,
        stages=["CS1:002(最后)", "CS2:002(最后)"]
    )
    df_cs_force = beam_force.process_construction_results(cs_force_results)
    beam_force.plot_results(df_cs_force, component="Moment-y")
    
    # 应力结果
    cs_stress_results = beam_stress.extract_construction(
        elems="1 to 31",
        load_case="合计(CS)",
        force_unit="N",
        dist_unit="mm",
        format_style="Scientific",
        decimal_places=6,
        stages=["CS1:002(最后)", "CS2:002(最后)"]
    )
    df_cs_stress = beam_stress.process_construction_results(cs_stress_results)
    beam_stress.plot_results(df_cs_stress, component="Cb(min/max)")
    '''
'''  
    # 6. 节点和单元操作示例
    # 使用预处理器
    node_processor = midas.pre.node
    beam = midas.pre.beam
    cable = midas.pre.cable
    
    # 查询节点
    nodes = node_processor.query()
    print("节点查询结果:", nodes)
    
    # 创建新节点
    node_processor.create({
        "Assign": {
            "33": {"X": 16, "Y": 0, "Z": 0}
        }
    })
    
    # 更新节点
    node_processor.update({
        "Assign": {
            "33": {"X": 17, "Y": 0, "Z": 0}
        }
    })
    
    # 删除节点
    node_processor.delete_single(33)
    
    # 查询单元
    elements = beam.query()
    print("单元查询结果:", elements)
    
    # 创建新单元
    beam.create(element_id=32, matl=1, sect=1, nodes=[30, 31])
    
    # 删除单元
    beam.delete_single(32)
    
    # 创建索单元示例
    cable.create(
        element_id=32,
        matl=1,
        sect=1,
        nodes=[15, 30],
        angle=0,
        cable_type=1,
        tens=1500
    )
    cable.delete_single(32)
    
    # 7. 保存文件
    midas.operations.save_file(file_path)
'''
if __name__ == "__main__":
    run_beam_analysis() 