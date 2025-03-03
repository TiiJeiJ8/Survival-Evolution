# Survival & Evolution 生存与进化

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Pygame](https://img.shields.io/badge/Pygame-2.0+-green)
![GPU](https://img.shields.io/badge/GPU_Acceleration-Optional-brightgreen)

一个基于Python/Pygame的生物进化模拟系统，包含动态生态系统与硬件加速渲染支持。  
A Python/Pygame biological evolution simulation system with dynamic ecosystem and GPU-accelerated rendering.

---

## 🌟 功能特性 | Features
### 当前实现 | Implemented
- **动态生物行为**  
  - 🦁 捕食者：智能追逐/能量繁殖
  - 🦌 被捕食者：环境感知/紧急逃生/植物觅食
  - 🌿 植被：集群生成/能量补给/动态再生
- **感知系统**
  - 视觉：捕食者220°广角视野 vs 被捕食者85°聚焦视野
  - 听觉：动态距离检测与威胁响应
  - 能量：饥饿阈值驱动的紧急行为
- **高性能渲染**
  - 硬件加速表面（HWSURFACE）
  - 双缓冲技术消除闪烁
  - 自动回退软件渲染保障兼容性

### 未来计划 | Roadmap
- 🧠 **智能决策模块**
  - 基于神经网络的捕食策略优化
  - 遗传算法驱动的适应性进化
  - 环境压力驱动的行为权重调整
- 🌱 **生态系统动态**
  - 生物集群生成与消亡
  - 生态系统平衡与稳定性
  - 环境变化对生物的影响
- ⚡ **性能增强**
  - 多线程生物逻辑处理
  - 精灵批处理渲染优化
  - 动态LOD细节分级
- 🔬 **科学分析**
  - 基因漂变可视化
  - 生态系统能量流分析
  - 种群生存曲线生成

---

## 🚀 快速开始 | Quick Start
### 依赖安装 | Requirements
```bash
pip install pygame numpy
```

### 运行模拟 | Run Simulation
```bash
python startUp.py
```
**默认生态参数**  
| 物种            | 数量 | 特性                 |
| --------------- | ---- | -------------------- |
| 捕食者 Predator | 10   | 高攻击性/低繁殖阈值  |
| 被捕食者 Prey   | 50   | 快速繁殖/环境敏感    |
| 植被 Plants     | 200  | 集群生成/每簇3-5单位 |

---

## ⚡ 性能优化 | Performance
### GPU加速渲染
```python
# UI_design.py 核心实现
self.screen = pygame.display.set_mode(
    (width, height),
    pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.SCALED  # 硬件加速标志
)
```
**验证加速状态**  
```bash
# 控制台启动时显示（示例）
GPU Acceleration: Enabled (OpenGL)
Current graphics driver: opengl
```

### 优化建议
1. **强制启用加速**（仅限支持设备）：
   ```python
   pygame.display.set_mode(flags=pygame.FULLSCREEN | pygame.HWSURFACE)
   ```
2. **性能调优参数**：
   - 垂直同步：`vsync=1` 消除画面撕裂
   - 分辨率缩放：`pygame.SCALED` 适配高分屏
   - 脏矩形更新：`pygame.sprite.RenderUpdates()`

**效能基准**  
| 场景规模 | 软件渲染 FPS | GPU加速 FPS | 提升幅度 |
| -------- | ------------ | ----------- | -------- |
| 100生物  | 58           | 60          | +3%      |
| 1000生物 | 42           | 59          | +40%     |
| 5000生物 | 11           | 33          | 200%     |

---

## 🗂️ 项目架构 | Architecture
```bash
.
├── creature_def.py    # 生物核心逻辑（感知/行为/繁殖）
├── vegetation.py      # 植被生成与集群管理
├── UI_design.py       # 渲染系统与GPU加速层
├── startUp.py         # 生态参数初始化
├── README.md          # 项目介绍与使用说明
└── ...
```

---

## 🤝 参与贡献 | Contributing
欢迎通过以下方式改进项目：
- **算法优化**：决策树/路径规划/感知模型
- **渲染增强**：Shader特效/粒子系统/LOD
- **生态扩展**：地形系统/天气模拟/基因突变

提交PR时请遵循：
1. 新功能添加对应单元测试
2. GPU相关修改需验证多驱动兼容性
3. 重大变更更新性能基准数据

---

## 📜 许可协议 | License
[MIT License](LICENSE) © 2025 TiiJeiJ8

---

>"真正的进化发生在代码之外" —— 项目格言
>
>"生命会找到自己的出路" ——《侏罗纪公园》
>
>"Life finds a way." —— Jurassic Park
>
>"True evolution happens beyond code." —— Project Motto