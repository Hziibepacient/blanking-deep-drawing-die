# 三维展示说明

2026-11-13 按原始 STEP 文件重新制作，替换课程报告截图。装配图与两张零件图保持不变。

## 几何与视图

输入：`cad/assembly.step`。使用 Open CASCADE 7.9.3 读取，提取 43 个实体，逐个执行 `BRepCheck_Analyzer`，结果均有效。完整模型渲染网格包含 114,350 个三角形；网格化线性偏差设为 0.12 mm、角度偏差 0.22 rad。

| 展示图 | 生成方式 |
| --- | --- |
| 装配整体 | 保留原始装配位置，仅统一旋转/缩放场景坐标 |
| 分层结构 | 保留各实体形状与方向，沿模具工作方向将实体分组平移 0、72、162、265 mm；为展示分组，不等同于拆装工艺或工作行程 |
| 工作区剖切 | 用通过工作轴线的平面保留一侧实体，执行真实布尔交集；新形成的截面用暖色区分 |

三张图使用同一组相机方向、棚拍式面积光源和展示材质，在 Blender 5.2.3 / Cycles 中渲染。为让边缘反光清楚，添加 0.6 mm 的渲染倒角修饰器；该修饰器只作用于展示网格，不改 STEP 文件，也不表示原始模型全部具有该倒角。

配色、反光、光照和背景属于视觉表达，不构成材料、表面处理、尺寸或强度标注。模型有效性检查不代表没有装配干涉，也不等于原生 CAD 特征可重建或模具可制造。

## 重现

脚本位于 `scripts/visualization/`。这套流程与无依赖的算术复核脚本分开；只有重新制作展示图才需要 CAD 与渲染依赖。

依赖：Python 3.12、`cadquery-ocp-novtk==7.9.3.1.1`、Pillow、Blender 5.2。排版脚本默认使用 Windows 的微软雅黑与 Segoe UI 字体；其他系统需替换字体路径。

在 `scripts/visualization/` 目录执行：

```bash
python export_geometry.py
blender --background --factory-startup --python render_geometry.py -- assembly
blender --background --factory-startup --python render_geometry.py -- exploded
blender --background --factory-startup --python render_geometry.py -- section
python compose_portfolio.py
```

中间网格、Blender 场景和透明底原图保存在脚本目录，仅最终三张排版 PNG 收录到 `assets/`。原始 DWG、STEP、PDF 与二维预览图的内容和校验值保持不变。
