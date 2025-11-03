# HAIGC Mask - ComfyUI 专业遮罩处理工具集

<div align="center">

[中文](#中文文档) | [English](#english-documentation)

一套功能强大的 ComfyUI 遮罩处理节点集合，提供遮罩生成、变换、调整、选择和比较等完整功能。

</div>

---

## 中文文档

### 📦 节点列表

本工具集包含 5 个专业遮罩处理节点：

1. **🎨 遮罩生成器** - 从零创建各种形状的遮罩
2. **📐 遮罩尺寸调整** - 精确调整遮罩尺寸和位置
3. **🔄 遮罩变换** - 翻转、旋转、缩放等变换操作
4. **🎯 多遮罩选择器** - 智能选择和排序遮罩
5. **⚖️ 遮罩比较节点** - 对比两个遮罩的差异

---

## 1. 🎨 遮罩生成器 (HAIGC)

### 功能概述

从头创建各种专业级遮罩，支持 8 种形状类型和丰富的参数控制。使用先进的 SDF（有向距离场）算法，实现完美的抗锯齿效果。

### 支持的形状类型

| 形状 | 说明 | 特色功能 |
|------|------|---------|
| **矩形** | 标准矩形/正方形 | 支持圆角、旋转 |
| **圆形** | 完美的圆形 | SDF 算法，完美抗锯齿 |
| **椭圆** | 可旋转的椭圆 | 独立控制长轴/短轴 |
| **多边形** | 3-20 边的正多边形 | 可旋转、可调边数 |
| **星形** | 可调角数的星形 | 内外半径独立控制 |
| **渐变** | 线性/径向/角度渐变 | 平滑过渡效果 |
| **噪声** | 柏林/随机/云彩噪声 | 有机纹理生成 |
| **棋盘** | 棋盘格图案 | 可调格子数量 |

### 核心参数说明

#### 基础参数
- **画布宽度/高度**: 64-8192px，步进 8px
- **形状类型**: 选择要生成的形状
- **操作模式**: 新建/叠加/相交/差集/排除
- **中心X/Y**: 0.0-1.0，相对画布的位置

#### 矩形专用参数
- **宽度 (矩形)**: 0.0-1.0，矩形宽度占比
- **高度 (矩形)**: 0.0-1.0，矩形高度占比
- **圆角半径 (矩形)**: 0-200px，圆角大小
- **旋转角度**: -180°到180°

#### 圆形/椭圆参数
- **半径 (圆形/多边形/星形)**: 0.0-1.0，圆形大小
- **长轴 (椭圆)**: 0.0-1.0，椭圆横向尺寸
- **短轴 (椭圆)**: 0.0-1.0，椭圆纵向尺寸

#### 多边形/星形参数
- **边数 (多边形/星形)**: 3-20，多边形边数或星形角数
- **内半径 (星形)**: 0.0-1.0，星形内角深度
- **旋转角度**: -180°到180°

#### 渐变参数
- **渐变类型 (渐变)**: 线性/径向/角度
- **渐变角度 (渐变)**: -180°到180°
- **反转渐变 (渐变)**: 是/否

#### 噪声参数
- **噪声类型 (噪声)**: 柏林噪声/随机/云彩
- **噪声强度 (噪声)**: 0.0-1.0，噪声浓度
- **噪声缩放 (噪声)**: 0.1-20.0，噪声细节

#### 棋盘参数
- **格子数X (棋盘)**: 1-50，横向格子数
- **格子数Y (棋盘)**: 1-50，纵向格子数

#### 高级参数
- **羽化边缘**: 0.0-100.0，边缘柔化程度
- **抗锯齿强度**: 关闭/标准/高质量/超高质量
- **反转遮罩**: 是/否，反转黑白

### 使用示例

#### 示例 1：创建圆角矩形
```
形状类型: 矩形
宽度 (矩形): 0.6
高度 (矩形): 0.4
圆角半径 (矩形): 50
旋转角度: 15°
抗锯齿强度: 高质量
```

#### 示例 2：创建五角星
```
形状类型: 星形
半径 (圆形/多边形/星形): 0.4
内半径 (星形): 0.2
边数 (多边形/星形): 5
旋转角度: 0°
```

#### 示例 3：叠加多个遮罩
```
1. 创建第一个圆形遮罩（操作模式: 新建）
2. 连接到"输入遮罩"
3. 创建第二个矩形（操作模式: 叠加）
→ 结果：两个形状合并
```

### 输出
- **遮罩**: ComfyUI 标准遮罩格式
- **生成信息**: 详细的参数和统计信息

---

## 2. 📐 遮罩尺寸调整 (HAIGC)

### 功能概述

精确调整遮罩的尺寸和位置，支持多种插值方法和对齐方式，自动处理边界问题。

### 主要功能

#### 基准方式
- **遮罩区域**: 基于遮罩内容自动计算
- **画布尺寸**: 基于目标尺寸调整

#### 插值方法
- **最近邻**: 保持硬边缘，适合精确遮罩
- **双线性**: 平滑过渡，通用选择
- **双三次**: 高质量缩放，最佳效果
- **兰索斯**: 专业级别，保持细节

#### 对齐方式
9 种对齐位置：
```
左上  居中上  右上
左中  居中    右中
左下  居中下  右下
```

### 核心参数

- **目标宽度/高度**: 输出遮罩尺寸
- **基准方式**: 遮罩区域/画布尺寸
- **保持宽高比**: 是/否
- **插值方法**: 最近邻/双线性/双三次/兰索斯
- **对齐方式**: 9 种位置选择
- **边缘留白**: 0-500px，四周留白

### 使用场景

1. **批量调整尺寸**: 统一遮罩尺寸
2. **保持比例缩放**: 避免变形
3. **智能对齐**: 精确控制位置
4. **边界处理**: 自动添加留白

---

## 3. 🔄 遮罩变换 (HAIGC)

### 功能概述

对遮罩执行各种几何变换操作，包括翻转、旋转、缩放、偏移等。

### 主要功能

#### 启用旋转
- **旋转角度**: -180°到180°
- **插值方法**: 最近邻/双线性/双三次
- **对齐方式**: 居中/自定义
- **裁剪到边框**: 自动裁剪/保留全部

#### 启用缩放
- **缩放比例**: 独立控制 X/Y 轴
- **保持宽高比**: 同步缩放

#### 启用偏移
- **X偏移**: -2000 到 2000 像素
- **Y偏移**: -2000 到 2000 像素

#### 启用翻转
- **水平翻转**: 左右镜像
- **垂直翻转**: 上下镜像

### 高级功能

- **羽化角度**: 0-50，边缘柔化
- **启用偏移**: 平移遮罩位置
- **边界填充**: 0-500，边缘填充
- **裁剪到边框**: 自动裁剪超出部分

### 使用示例

#### 示例 1：旋转并居中
```
启用旋转: 是
旋转角度: 45°
对齐方式: 居中
裁剪到边框: 是
```

#### 示例 2：镜像翻转
```
启用翻转: 是
水平翻转: 是
垂直翻转: 否
```

#### 示例 3：缩放并偏移
```
启用缩放: 是
缩放X: 1.5
缩放Y: 1.5
启用偏移: 是
X偏移: 100
Y偏移: -50
```

---

## 4. 🎯 多遮罩选择器 (HAIGC)

### 功能概述

从多个输入遮罩中智能选择和排序，支持多种选择策略和排序方式。

### 排序方向

- **从左到右**: 按 X 坐标排序
- **从右到左**: 按 X 坐标倒序
- **从上到下**: 按 Y 坐标排序
- **从下到上**: 按 Y 坐标倒序
- **按面积**: 从大到小
- **按面积（逆序）**: 从小到大

### 选择模式

- **单个遮罩**: 选择一个特定遮罩
- **范围选择**: 选择一段连续遮罩
- **多个选择**: 选择多个指定遮罩
- **排除模式**: 排除某些遮罩

### 核心参数

- **排序方向**: 6 种排序方式
- **选择模式**: 单个/范围/多个/排除
- **遮罩索引**: 指定遮罩序号（从 0 开始）
- **选择数量**: 选择多少个遮罩
- **最小面积**: 过滤小于此面积的遮罩

### 输出信息

- **详细信息**: 遮罩总数、选择数量
- **遮罩总数**: 输入遮罩的数量
- **遮罩列表**: 所有遮罩的详细信息

### 使用场景

1. **批量处理**: 按顺序处理多个遮罩
2. **智能筛选**: 按面积/位置筛选
3. **精确选择**: 指定特定遮罩
4. **排除干扰**: 排除不需要的遮罩

---

## 5. ⚖️ 遮罩比较节点 (HAIGC)

### 功能概述

对比两个遮罩的差异，支持多种比较模式，输出差异遮罩和详细统计信息。

### 比较模式

| 模式 | 说明 | 应用场景 |
|------|------|---------|
| **Dice系数** | 相似度评分 (0-1) | 评估重叠程度 |
| **IoU** | 交并比 | 目标检测评估 |
| **差异区域** | 仅显示不同部分 | 找出差异 |
| **重叠区域** | 仅显示重叠部分 | 找出共同点 |
| **边缘对比** | 对比边缘差异 | 精确度检查 |

### 输出信息

- **差异遮罩**: 可视化差异结果
- **得分**: 数值化的相似度/差异度
- **比较信息**: 详细的统计数据
  - 相似度/差异度百分比
  - 重叠面积
  - 差异面积
  - 各区域像素数

### 使用场景

1. **质量检查**: 对比生成结果与目标
2. **迭代优化**: 追踪优化进度
3. **批量评估**: 自动化质量评分
4. **差异分析**: 找出具体差异位置

---

## 💡 使用技巧

### 1. 组合使用多个节点

```
遮罩生成器 → 遮罩变换 → 遮罩尺寸调整 → 最终输出
```

### 2. 利用操作模式创建复杂形状

```
1. 创建圆形 (操作模式: 新建)
2. 叠加矩形 (操作模式: 叠加)
3. 减去小圆 (操作模式: 差集)
→ 创建复杂组合形状
```

### 3. 批量处理遮罩

```
多个输入 → 多遮罩选择器 (排序) → 遮罩变换 → 统一输出
```

### 4. 质量控制流程

```
生成遮罩 → 遮罩比较节点 (与目标对比) → 评估分数 → 迭代优化
```

---

## 🔧 技术特点

### 1. SDF 距离场算法
- 完美的抗锯齿效果
- 平滑的边缘过渡
- 高质量的形状渲染

### 2. 智能参数标注
- 每个参数都标注了适用形状
- 清晰的功能分组
- 避免参数混淆

### 3. 向后兼容
- 支持旧版参数名
- 工作流无缝迁移
- 不破坏现有项目

### 4. 详细的输出信息
- 实时显示参数状态
- 统计数据（面积、覆盖率）
- 便于调试和优化

---

## 📦 安装方法

### 方法 1: 通过 ComfyUI Manager（推荐）

1. 打开 ComfyUI Manager
2. 搜索 "HAIGC Mask"
3. 点击安装
4. 重启 ComfyUI

### 方法 2: 手动安装

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/your-repo/haigc_mask.git
cd haigc_mask
pip install -r requirements.txt（便携python包：python -m pip install -r requirements.txt）
```

### 方法 3: 直接下载

1. 下载本仓库的 ZIP 文件
2. 解压到 `ComfyUI/custom_nodes/haigc_mask/`
3. 安装依赖：pip install -r requirements.txt（便携python包：python -m pip install -r requirements.txt）
4. 重启 ComfyUI

---

## 🔄 更新日志

### v1.1.0 (最新)
- ✅ 修复圆角矩形功能，使用 SDF 算法实现真正的圆角
- ✅ 为矩形添加旋转角度支持
- ✅ 所有参数添加功能标注（如"宽度 (矩形)"）
- ✅ 改进抗锯齿效果，统一使用 SDF 渲染
- ✅ 完善的羽化支持
- ✅ 向后兼容旧版参数名

### v1.0.0
- 初始发布
- 5 个核心遮罩处理节点
- 8 种基础形状生成
- 多种变换和调整功能

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

---

## 🙏 致谢

感谢 ComfyUI 社区的支持和反馈！

---

## 💖 支持项目

<div align="center">

**如果支持我持续维护，可扫码支持，感谢！**

<img src="docs/support_qrcode.png" width="200" alt="支持二维码"/>

</div>

---

<div align="center">

## comfyui工作流云平台推荐，点击链接注册送1000点算力：https://www.runninghub.cn/user-center/1887871050510716930/userPost?inviteCode=rh-v1127
## 国际站，点击链接注册送1000点算力：https://www.runninghub.ai/user-center/1939305513756864513/userPost?inviteCode=rh-v1127

**如果这个项目对你有帮助，请给个 ⭐ Star！**

</div>

---

# English Documentation

## 📦 Node List

This toolkit includes 5 professional mask processing nodes:

1. **🎨 Mask Generator** - Create masks from scratch with various shapes
2. **📐 Mask Resize** - Precise mask size and position adjustment
3. **🔄 Mask Transform** - Flip, rotate, scale and other transformations
4. **🎯 Multi-Mask Selector** - Smart mask selection and sorting
5. **⚖️ Mask Comparator** - Compare differences between two masks

---

## 1. 🎨 Mask Generator (HAIGC)

### Overview

Create professional-grade masks from scratch with 8 shape types and rich parameter controls. Uses advanced SDF (Signed Distance Field) algorithm for perfect anti-aliasing.

### Supported Shapes

- **Rectangle**: Standard rectangles with rounded corners and rotation support
- **Circle**: Perfect circles with SDF anti-aliasing
- **Ellipse**: Rotatable ellipses with independent axis control
- **Polygon**: Regular polygons with 3-20 sides
- **Star**: Stars with adjustable inner/outer radius
- **Gradient**: Linear/Radial/Angular gradients
- **Noise**: Perlin/Random/Cloud noise patterns
- **Checkerboard**: Customizable checkerboard patterns

### Key Features

#### Shape-Specific Parameters

Parameters are clearly labeled with their applicable shapes:
- `Width (Rectangle)` - Only for rectangles
- `Radius (Circle/Polygon/Star)` - For circles, polygons, and stars
- `Major Axis (Ellipse)` - Only for ellipses
- `Rotation Angle (Rectangle/Ellipse/Polygon/Star)` - For rotatable shapes

#### Advanced Features

1. **SDF Algorithm**: Perfect anti-aliasing for smooth edges
2. **Operation Modes**: New/Union/Intersect/Difference/Exclude
3. **Anti-aliasing Levels**: Off/Standard/High Quality/Ultra High Quality
4. **Feathering**: 0-100px edge softening
5. **Statistical Info**: Real-time area, coverage, and mean value

### Parameters Reference

#### Rectangle Parameters
- Width (Rectangle): 0.0-1.0
- Height (Rectangle): 0.0-1.0
- Corner Radius (Rectangle): 0-200px
- Rotation Angle: -180° to 180°

#### Circle/Ellipse Parameters
- Radius (Circle/Polygon/Star): 0.0-1.0
- Major Axis (Ellipse): 0.0-1.0
- Minor Axis (Ellipse): 0.0-1.0

#### Polygon/Star Parameters
- Sides (Polygon/Star): 3-20
- Inner Radius (Star): 0.0-1.0
- Rotation Angle: -180° to 180°

#### Gradient Parameters
- Gradient Type (Gradient): Linear/Radial/Angular
- Gradient Angle (Gradient): -180° to 180°
- Invert Gradient (Gradient): Yes/No

#### Noise Parameters
- Noise Type (Noise): Perlin/Random/Cloud
- Noise Strength (Noise): 0.0-1.0
- Noise Scale (Noise): 0.1-20.0

#### Checkerboard Parameters
- Grid Count X (Checkerboard): 1-50
- Grid Count Y (Checkerboard): 1-50

---

## 2. 📐 Mask Resize (HAIGC)

### Overview

Precisely adjust mask size and position with multiple interpolation methods and alignment options.

### Key Features

- **Base Methods**: Mask Region / Canvas Size
- **Interpolation**: Nearest / Bilinear / Bicubic / Lanczos
- **Alignment**: 9 position options (top-left, center, bottom-right, etc.)
- **Aspect Ratio**: Preserve or ignore
- **Edge Padding**: 0-500px border space

---

## 3. 🔄 Mask Transform (HAIGC)

### Overview

Perform various geometric transformations on masks including flip, rotate, scale, and offset.

### Transformation Types

1. **Rotation**: -180° to 180° with multiple interpolation methods
2. **Scaling**: Independent X/Y scaling with aspect ratio lock
3. **Offset**: -2000 to 2000 pixels in X/Y directions
4. **Flipping**: Horizontal and/or vertical flip

### Advanced Options

- **Feather Angle**: 0-50 for edge softening
- **Crop to Frame**: Automatically crop overflow
- **Border Fill**: 0-500px padding

---

## 4. 🎯 Multi-Mask Selector (HAIGC)

### Overview

Intelligently select and sort from multiple input masks with various strategies.

### Sort Directions

- Left to Right / Right to Left
- Top to Bottom / Bottom to Top
- By Area (Largest First / Smallest First)

### Selection Modes

- Single Mask
- Range Selection
- Multiple Selection
- Exclude Mode

### Features

- Minimum area filtering
- Detailed statistics output
- Mask list information

---

## 5. ⚖️ Mask Comparator (HAIGC)

### Overview

Compare two masks and output difference visualization with detailed statistics.

### Comparison Modes

- **Dice Coefficient**: Similarity score (0-1)
- **IoU**: Intersection over Union
- **Difference Area**: Show only differences
- **Overlap Area**: Show only intersections
- **Edge Comparison**: Compare edge differences

### Outputs

- Difference mask visualization
- Numerical similarity/difference scores
- Detailed statistical information

---

## 💡 Usage Tips

### 1. Combine Multiple Nodes

```
Mask Generator → Transform → Resize → Final Output
```

### 2. Create Complex Shapes

```
1. Create circle (Mode: New)
2. Add rectangle (Mode: Union)
3. Subtract small circle (Mode: Difference)
→ Complex combined shapes
```

### 3. Batch Processing

```
Multiple Inputs → Multi-Mask Selector → Transform → Output
```

---

## 🔧 Technical Highlights

1. **SDF Distance Field Algorithm**: Perfect anti-aliasing
2. **Smart Parameter Labels**: Clear shape associations
3. **Backward Compatible**: Supports legacy parameter names
4. **Detailed Output Info**: Real-time statistics and debugging info

---

## 📦 Installation

### Method 1: ComfyUI Manager (Recommended)

1. Open ComfyUI Manager
2. Search "HAIGC Mask"
3. Click Install
4. Restart ComfyUI

### Method 2: Manual Installation

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/your-repo/haigc_mask.git
cd haigc_mask
pip install -r requirements.txt
```

### Method 3: Direct Download

1. Download ZIP from this repository
2. Extract to `ComfyUI/custom_nodes/haigc_mask/`
3. Install dependencies: `pip install numpy opencv-python scipy torch`
4. Restart ComfyUI

---

## 🔄 Changelog

### v1.1.0 (Latest)
- ✅ Fixed rounded rectangle with SDF algorithm
- ✅ Added rotation support for rectangles
- ✅ Added shape labels to all parameters
- ✅ Improved anti-aliasing with unified SDF rendering
- ✅ Enhanced feathering support
- ✅ Backward compatible with old parameter names

### v1.0.0
- Initial release
- 5 core mask processing nodes
- 8 basic shape types
- Multiple transformation features

---

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) file for details.

---

## 💖 Support the Project

<div align="center">

**If you'd like to support continued maintenance, scan the code below. Thank you!**

<img src="docs/support_qrcode.png" width="200" alt="Support QR Code"/>

</div>

---

<div align="center">

## Comfyui workflow cloud platform recommendation, click on the link to register and receive 1000 computing power points：https://www.runninghub.cn/user-center/1887871050510716930/userPost?inviteCode=rh-v1127
## International website, click on the link to register and receive 1000 computing power points：https://www.runninghub.ai/user-center/1939305513756864513/userPost?inviteCode=rh-v1127


**If this project helps you, please give it a ⭐ Star!**

Made with ❤️ by HAIGC Team

</div>

"# haigc_mask" 
"# haigc_mask" 
