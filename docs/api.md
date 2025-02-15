# API 文档

## MidasCivil 类

主接口类，提供对 MIDAS Civil 所有功能的访问。

### 属性

- `operations`: 基本操作接口
- `pre`: 预处理器接口
- `post`: 后处理器接口
- `construction`: 施工阶段处理器接口

### 预处理器接口

包含以下子接口：

- `node`: 节点处理
- `beam`: 梁单元处理
- `truss`: 桁架单元处理
- `cable`: 索单元处理
- `support`: 支承处理
- `spring`: 弹簧支承处理
- `rigid_link`: 刚性连接处理
- `elastic_link`: 弹性连接处理
- `static_loads`: 静力荷载处理
- `temperature_loads`: 温度荷载处理
- `prestress_loads`: 预应力荷载处理

### 施工阶段处理器接口

提供施工阶段相关的功能：

- `query_construction_stages()`: 查询当前施工阶段信息 