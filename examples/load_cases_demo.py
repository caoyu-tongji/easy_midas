from structural_analysis import (
    StaticLoadsProcessor,
    TemperatureLoadsProcessor,
    PrestressLoadsProcessor,
    ConstructionStageProcessor
)


def demo_static_loads():
    """静力荷载工况示例"""
    static_loads = StaticLoadsProcessor()
    
    print("\n=== 静力荷载工况操作 ===")
    
    # 添加恒载工况
    static_loads.add_load_case(
        case_id=11,
        name="DL",
        case_type="D",
        description="Dead Loads"
    )
    
    # 添加活载工况
    static_loads.add_load_case(
        case_id=12,
        name="LL",
        case_type="L",
        description="Live Loads"
    )
    
    # 查询所有工况
    cases = static_loads.query()
    print("当前工况:", cases)
    
    # 更新工况
    static_loads.update_load_case(
        case_id=11,
        name="DL1",
        description="Updated Dead Loads"
    )
    
    print("=== 静力荷载工况操作完成 ===\n")
    
    # 自重荷载示例
    print("\n=== 自重荷载操作 ===")
    
    # 添加自重荷载
    static_loads.add_self_weight(
        case_id=11,
        load_case="DL1",
        group_name="",
        fv=[0, 0, -1]
    )
    
    # 查询自重荷载
    weights = static_loads.query()
    print("当前自重荷载:", weights)
    
    print("=== 自重荷载操作完成 ===\n")

def demo_temperature_loads():
    """温度荷载示例"""
    temp_loads = TemperatureLoadsProcessor()
    
    print("\n=== 温度梯度荷载操作 ===")
    
    # 添加梁单元温度梯度
    beam_temps = [
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
    temp_loads.add_beam_gradient_temp(2, beam_temps)
    
    # 查询温度梯度荷载
    temps = temp_loads.query()
    print("当前温度梯度荷载:", temps)
    
    print("=== 温度梯度荷载操作完成 ===\n")

def demo_prestress_loads():
    """预应力荷载示例"""
    prestress = PrestressLoadsProcessor()
    
    print("\n=== 钢束预应力操作 ===")
    
    # 添加预应力
    prestress.add_tendon_prestress(
        tendon_id=2,            # 钢束编号
        tendon_name="TENDON1",
        load_case="预应力",
        begin_value=1395,       # 起点预应力
        end_value=1395,         # 终点预应力
        group_name="施工41张拉钢束_钢混_2",
        prestress_type="STRESS",
        tension_order="BOTH",
        grouting_stage=1
    )
    
    # 查询预应力
    prestresses = prestress.query()
    print("当前钢束预应力:", prestresses)
    
    # 更新预应力
    prestress.update_tendon_prestress(
        tendon_id=2,
        tendon_name="TENDON1",
        load_case="预应力",
        begin_value=1340,       # 起点预应力
        end_value=1340,         # 终点预应力
        group_name="施工41张拉钢束_钢混_2",
        prestress_type="STRESS",
        tension_order="BOTH",
        grouting_stage=1
    )
    
    print("=== 钢束预应力操作完成 ===\n")
    
    print("\n=== 初拉力操作 ===")
    
    # 添加初拉力
    prestress.add_initial_tension(
        elem_id=2001,
        load_case="初拉力",
        tension=130,
        group_name="C12"
    )
    
    # 查询初拉力
    tensions = prestress.query()
    print("当前初拉力:", tensions)
    
    # 更新初拉力
    prestress.update_initial_tension(
        elem_id=2001,
        load_case="初拉力",
        tension=140,
        group_name="C12"
    )
    
    print("=== 初拉力操作完成 ===\n")

def demo_construction_stages():
    """施工阶段示例"""
    stages_processor = ConstructionStageProcessor()
    
    print("\n=== 施工阶段查询 ===")
    
    # 查询施工阶段
    stages = stages_processor.query_construction_stages()
    print("当前施工阶段:", stages)
    
    print("=== 施工阶段查询完成 ===\n")

def main():
    """主函数"""
    print("=== 开始荷载示例 ===")
    
    # 运行静力荷载示例
    demo_static_loads()
    
    # 运行温度荷载示例
    demo_temperature_loads()
    
    # 运行预应力荷载示例
    demo_prestress_loads()
    
    # 运行施工阶段示例
    demo_construction_stages()
    
    print("=== 荷载示例完成 ===")

if __name__ == "__main__":
    main() 