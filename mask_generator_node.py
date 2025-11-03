"""
遮罩生成器节点
作者: HAIGC Mask Development Team
功能: 从头创建各种形状的遮罩（圆形、矩形、多边形、渐变等）
"""

import torch
import numpy as np
import cv2

class MaskGeneratorNode:
    """遮罩生成器 - 创建各种形状的遮罩"""
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "画布宽度": ("INT", {"default": 512, "min": 64, "max": 8192, "step": 8, "display": "number"}),
                "画布高度": ("INT", {"default": 512, "min": 64, "max": 8192, "step": 8, "display": "number"}),
                "形状类型": (["矩形", "圆形", "椭圆", "多边形", "星形", "渐变", "噪声", "棋盘"], 
                          {"default": "圆形"}),
            },
            "optional": {
                # === 输入遮罩 ===
                "输入遮罩": ("MASK",),
                "操作模式": (["新建", "叠加", "相交", "差集", "排除"], {"default": "新建"}),
                # === 通用参数 ===
                "中心X": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01, "display": "slider"}),
                "中心Y": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01, "display": "slider"}),
                
                # === 矩形参数 ===
                "宽度 (矩形)": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01, "display": "slider"}),
                "高度 (矩形)": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01, "display": "slider"}),
                "圆角半径 (矩形)": ("INT", {"default": 0, "min": 0, "max": 200, "step": 1, "display": "number"}),
                
                # === 圆形/多边形/星形参数 ===
                "半径 (圆形/多边形/星形)": ("FLOAT", {"default": 0.3, "min": 0.0, "max": 1.0, "step": 0.01, "display": "slider"}),
                
                # === 椭圆参数 ===
                "长轴 (椭圆)": ("FLOAT", {"default": 0.3, "min": 0.0, "max": 1.0, "step": 0.01, "display": "slider"}),
                "短轴 (椭圆)": ("FLOAT", {"default": 0.2, "min": 0.0, "max": 1.0, "step": 0.01, "display": "slider"}),
                
                # === 旋转参数 ===
                "旋转角度 (矩形/椭圆/多边形/星形)": ("FLOAT", {"default": 0.0, "min": -180.0, "max": 180.0, "step": 1.0, "display": "number"}),
                
                # === 多边形/星形参数 ===
                "边数 (多边形/星形)": ("INT", {"default": 5, "min": 3, "max": 20, "step": 1, "display": "number"}),
                "内半径 (星形)": ("FLOAT", {"default": 0.15, "min": 0.0, "max": 1.0, "step": 0.01, "display": "slider"}),
                
                # === 渐变参数 ===
                "渐变类型 (渐变)": (["线性", "径向", "角度"], {"default": "线性"}),
                "渐变角度 (渐变)": ("FLOAT", {"default": 0.0, "min": -180.0, "max": 180.0, "step": 1.0, "display": "number"}),
                "反转渐变 (渐变)": ("BOOLEAN", {"default": False, "label_on": "是", "label_off": "否"}),
                
                # === 噪声参数 ===
                "噪声类型 (噪声)": (["柏林噪声", "随机", "云彩"], {"default": "柏林噪声"}),
                "噪声强度 (噪声)": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01, "display": "slider"}),
                "噪声缩放 (噪声)": ("FLOAT", {"default": 5.0, "min": 0.1, "max": 20.0, "step": 0.1, "display": "number"}),
                
                # === 棋盘参数 ===
                "格子数X (棋盘)": ("INT", {"default": 8, "min": 1, "max": 50, "step": 1, "display": "number"}),
                "格子数Y (棋盘)": ("INT", {"default": 8, "min": 1, "max": 50, "step": 1, "display": "number"}),
                
                # === 边缘处理与抗锯齿 ===
                "羽化边缘": ("FLOAT", {"default": 2.0, "min": 0.0, "max": 100.0, "step": 0.1, "display": "slider"}),
                "抗锯齿强度": (["关闭", "标准", "高质量", "超高质量"], {"default": "标准"}),
                "反转遮罩": ("BOOLEAN", {"default": False, "label_on": "是", "label_off": "否"}),
            }
        }
    
    RETURN_TYPES = ("MASK", "STRING")
    RETURN_NAMES = ("遮罩", "生成信息")
    FUNCTION = "generate_mask"
    CATEGORY = "遮罩处理/HAIGC"
    
    def create_rectangle(self, w, h, center_x, center_y, width, height, corner_radius, angle=0.0, feather=2.0):
        """创建矩形遮罩（支持圆角和旋转，使用SDF距离场）"""
        # 计算实际坐标和尺寸
        cx = center_x * w
        cy = center_y * h
        rect_w = width * w
        rect_h = height * h
        
        # 创建坐标网格
        y_coords, x_coords = np.ogrid[:h, :w]
        y_grid = y_coords - cy
        x_grid = x_coords - cx
        
        # 如果有旋转角度，旋转坐标系
        if angle != 0.0:
            angle_rad = np.radians(-angle)
            cos_a = np.cos(angle_rad)
            sin_a = np.sin(angle_rad)
            
            x_rot = x_grid * cos_a - y_grid * sin_a
            y_rot = x_grid * sin_a + y_grid * cos_a
        else:
            x_rot = x_grid
            y_rot = y_grid
        
        # 计算到矩形边界的距离（SDF - Signed Distance Field）
        # 矩形的半宽和半高
        half_w = rect_w / 2.0
        half_h = rect_h / 2.0
        
        # 到矩形边缘的距离
        dx = np.abs(x_rot) - half_w + corner_radius
        dy = np.abs(y_rot) - half_h + corner_radius
        
        if corner_radius > 0:
            # 圆角矩形距离场
            # 外部距离：到最近圆角的距离
            outside_dist = np.sqrt(np.maximum(dx, 0)**2 + np.maximum(dy, 0)**2)
            # 内部距离
            inside_dist = np.minimum(np.maximum(dx, dy), 0)
            # 总距离
            dist = outside_dist + inside_dist - corner_radius
        else:
            # 普通矩形距离场
            dist = np.maximum(dx, dy)
        
        # 使用距离场创建平滑边缘
        edge_width = max(feather, 0.5)
        t = np.clip((-dist + edge_width/2) / edge_width, 0, 1)
        
        # 应用 smoothstep: 3t² - 2t³
        mask = t * t * (3.0 - 2.0 * t)
        
        return mask.astype(np.float32)
    
    def create_circle(self, w, h, center_x, center_y, radius, feather=2.0):
        """创建圆形遮罩（使用SDF距离场，完美抗锯齿）"""
        # 计算实际坐标
        cx = center_x * w
        cy = center_y * h
        r = radius * min(w, h)
        
        # 创建坐标网格
        y_coords, x_coords = np.ogrid[:h, :w]
        
        # 计算每个像素到圆心的距离
        dist_from_center = np.sqrt((x_coords - cx)**2 + (y_coords - cy)**2)
        
        # 使用Smoothstep函数创建平滑边缘
        edge_width = max(feather, 0.5)
        t = np.clip((r - dist_from_center + edge_width/2) / edge_width, 0, 1)
        
        # 应用smoothstep: 3t² - 2t³
        mask = t * t * (3.0 - 2.0 * t)
        
        return mask.astype(np.float32)
    
    def create_ellipse(self, w, h, center_x, center_y, major_axis, minor_axis, angle, feather=2.0):
        """创建椭圆遮罩（使用SDF距离场，完美抗锯齿）"""
        # 计算实际坐标
        cx = center_x * w
        cy = center_y * h
        axes_w = major_axis * w
        axes_h = minor_axis * h
        
        # 创建坐标网格
        y_coords, x_coords = np.ogrid[:h, :w]
        y_grid = y_coords - cy
        x_grid = x_coords - cx
        
        # 旋转坐标系
        angle_rad = np.radians(-angle)
        cos_a = np.cos(angle_rad)
        sin_a = np.sin(angle_rad)
        
        x_rot = x_grid * cos_a - y_grid * sin_a
        y_rot = x_grid * sin_a + y_grid * cos_a
        
        # 计算椭圆距离
        dist = np.sqrt((x_rot / axes_w)**2 + (y_rot / axes_h)**2)
        
        # 平滑边缘
        edge_width = max(feather, 0.5) / max(axes_w, axes_h)
        t = np.clip((1.0 - dist + edge_width/2) / edge_width, 0, 1)
        
        # smoothstep
        mask = t * t * (3.0 - 2.0 * t)
        
        return mask.astype(np.float32)
    
    def create_polygon(self, w, h, center_x, center_y, radius, sides, rotation):
        """创建多边形遮罩"""
        mask = np.zeros((h, w), dtype=np.uint8)
        
        cx = int(center_x * w)
        cy = int(center_y * h)
        r = int(radius * min(w, h))
        
        # 计算多边形顶点
        points = []
        for i in range(sides):
            angle = (2 * np.pi * i / sides) + np.radians(rotation)
            x = cx + int(r * np.cos(angle))
            y = cy + int(r * np.sin(angle))
            points.append([x, y])
        
        points = np.array(points, dtype=np.int32)
        cv2.fillPoly(mask, [points], 255)
        
        return mask.astype(np.float32) / 255.0
    
    def create_star(self, w, h, center_x, center_y, outer_radius, inner_radius, points, rotation):
        """创建星形遮罩"""
        mask = np.zeros((h, w), dtype=np.uint8)
        
        cx = int(center_x * w)
        cy = int(center_y * h)
        r_outer = int(outer_radius * min(w, h))
        r_inner = int(inner_radius * min(w, h))
        
        # 计算星形顶点（交替外半径和内半径）
        vertices = []
        for i in range(points * 2):
            angle = (np.pi * i / points) + np.radians(rotation)
            r = r_outer if i % 2 == 0 else r_inner
            x = cx + int(r * np.cos(angle))
            y = cy + int(r * np.sin(angle))
            vertices.append([x, y])
        
        vertices = np.array(vertices, dtype=np.int32)
        cv2.fillPoly(mask, [vertices], 255)
        
        return mask.astype(np.float32) / 255.0
    
    def create_gradient(self, w, h, gradient_type, angle, reverse):
        """创建渐变遮罩"""
        mask = np.zeros((h, w), dtype=np.float32)
        
        if gradient_type == "线性":
            # 线性渐变
            angle_rad = np.radians(angle)
            for i in range(h):
                for j in range(w):
                    # 计算点到渐变方向的投影
                    x_norm = (j - w/2) / (w/2)
                    y_norm = (i - h/2) / (h/2)
                    proj = x_norm * np.cos(angle_rad) + y_norm * np.sin(angle_rad)
                    # 归一化到0-1
                    value = (proj + 1.0) / 2.0
                    mask[i, j] = value
        
        elif gradient_type == "径向":
            # 径向渐变（从中心向外）
            cy, cx = h / 2, w / 2
            max_dist = np.sqrt((h/2)**2 + (w/2)**2)
            for i in range(h):
                for j in range(w):
                    dist = np.sqrt((i - cy)**2 + (j - cx)**2)
                    mask[i, j] = 1.0 - (dist / max_dist)
        
        elif gradient_type == "角度":
            # 角度渐变（圆锥形）
            cy, cx = h / 2, w / 2
            for i in range(h):
                for j in range(w):
                    angle_at_point = np.arctan2(i - cy, j - cx)
                    mask[i, j] = (angle_at_point + np.pi) / (2 * np.pi)
        
        if reverse:
            mask = 1.0 - mask
        
        return np.clip(mask, 0.0, 1.0)
    
    def create_noise(self, w, h, noise_type, strength, scale):
        """创建噪声遮罩"""
        if noise_type == "随机":
            # 纯随机噪声
            mask = np.random.rand(h, w).astype(np.float32)
        
        elif noise_type == "柏林噪声":
            # 简化的柏林噪声（使用多层随机）
            mask = np.zeros((h, w), dtype=np.float32)
            
            # 多尺度噪声叠加
            for octave in range(3):
                freq = 2 ** octave * scale
                amplitude = 0.5 ** octave
                
                # 生成随机噪声并缩放
                noise_h = max(4, int(h / freq))
                noise_w = max(4, int(w / freq))
                noise = np.random.rand(noise_h, noise_w)
                
                # 放大到原始尺寸
                noise_scaled = cv2.resize(noise, (w, h), interpolation=cv2.INTER_LINEAR)
                mask += noise_scaled * amplitude
            
            mask = mask / mask.max()  # 归一化
        
        elif noise_type == "云彩":
            # 云彩效果（柏林噪声 + 阈值）
            mask = np.zeros((h, w), dtype=np.float32)
            
            for octave in range(4):
                freq = 2 ** octave * scale * 0.5
                amplitude = 0.5 ** octave
                
                noise_h = max(4, int(h / freq))
                noise_w = max(4, int(w / freq))
                noise = np.random.rand(noise_h, noise_w)
                
                noise_scaled = cv2.resize(noise, (w, h), interpolation=cv2.INTER_CUBIC)
                mask += noise_scaled * amplitude
            
            mask = mask / mask.max()
            # 应用强度
            mask = np.power(mask, 1.0 / (strength + 0.1))
        
        return np.clip(mask * strength, 0.0, 1.0)
    
    def create_checkerboard(self, w, h, grid_x, grid_y):
        """创建棋盘遮罩"""
        mask = np.zeros((h, w), dtype=np.float32)
        
        cell_w = w / grid_x
        cell_h = h / grid_y
        
        for i in range(grid_y):
            for j in range(grid_x):
                if (i + j) % 2 == 0:
                    x1 = int(j * cell_w)
                    y1 = int(i * cell_h)
                    x2 = int((j + 1) * cell_w)
                    y2 = int((i + 1) * cell_h)
                    mask[y1:y2, x1:x2] = 1.0
        
        return mask
    
    def apply_feather(self, mask, feather_amount):
        """应用羽化"""
        if feather_amount <= 0:
            return mask
        
        from scipy.ndimage import gaussian_filter
        return gaussian_filter(mask, sigma=feather_amount)
    
    def generate_mask(self, 画布宽度, 画布高度, 形状类型, **kwargs):
        """主生成函数"""
        w, h = 画布宽度, 画布高度
        
        # 获取输入遮罩和操作模式
        输入遮罩 = kwargs.get('输入遮罩', None)
        操作模式 = kwargs.get('操作模式', '新建')
        
        # 如果有输入遮罩，使用其尺寸
        if 输入遮罩 is not None:
            if len(输入遮罩.shape) == 3:
                h, w = 输入遮罩.shape[1:3]
            else:
                h, w = 输入遮罩.shape[0:2]
        
        # 获取参数（兼容新旧参数名）
        中心X = kwargs.get('中心X', 0.5)
        中心Y = kwargs.get('中心Y', 0.5)
        宽度 = kwargs.get('宽度 (矩形)', kwargs.get('宽度', 0.5))
        高度 = kwargs.get('高度 (矩形)', kwargs.get('高度', 0.5))
        圆角半径 = kwargs.get('圆角半径 (矩形)', kwargs.get('圆角半径', 0))
        半径 = kwargs.get('半径 (圆形/多边形/星形)', kwargs.get('半径', 0.3))
        长轴 = kwargs.get('长轴 (椭圆)', kwargs.get('长轴', 0.3))
        短轴 = kwargs.get('短轴 (椭圆)', kwargs.get('短轴', 0.2))
        旋转角度 = kwargs.get('旋转角度 (矩形/椭圆/多边形/星形)', kwargs.get('旋转角度', 0.0))
        边数 = kwargs.get('边数 (多边形/星形)', kwargs.get('边数', 5))
        内半径 = kwargs.get('内半径 (星形)', kwargs.get('内半径', 0.15))
        渐变类型 = kwargs.get('渐变类型 (渐变)', kwargs.get('渐变类型', '线性'))
        渐变角度 = kwargs.get('渐变角度 (渐变)', kwargs.get('渐变角度', 0.0))
        反转渐变 = kwargs.get('反转渐变 (渐变)', kwargs.get('反转渐变', False))
        噪声类型 = kwargs.get('噪声类型 (噪声)', kwargs.get('噪声类型', '柏林噪声'))
        噪声强度 = kwargs.get('噪声强度 (噪声)', kwargs.get('噪声强度', 0.5))
        噪声缩放 = kwargs.get('噪声缩放 (噪声)', kwargs.get('噪声缩放', 5.0))
        格子数X = kwargs.get('格子数X (棋盘)', kwargs.get('格子数X', 8))
        格子数Y = kwargs.get('格子数Y (棋盘)', kwargs.get('格子数Y', 8))
        羽化边缘 = kwargs.get('羽化边缘', 2.0)
        抗锯齿强度 = kwargs.get('抗锯齿强度', '标准')
        反转遮罩 = kwargs.get('反转遮罩', False)
        
        info_lines = []
        info_lines.append(f"画布尺寸: {w}×{h}")
        if 输入遮罩 is not None:
            info_lines.append(f"操作模式: {操作模式}")
        info_lines.append(f"形状类型: {形状类型}")
        
        # 根据抗锯齿强度调整羽化值
        aa_multiplier = {"关闭": 0, "标准": 1.0, "高质量": 1.5, "超高质量": 2.0}
        实际羽化 = 羽化边缘 * aa_multiplier.get(抗锯齿强度, 1.0)
        
        # 生成基础形状
        if 形状类型 == "矩形":
            mask = self.create_rectangle(w, h, 中心X, 中心Y, 宽度, 高度, 圆角半径, 旋转角度, 实际羽化)
            info_lines.append(f"尺寸: {宽度:.2f}×{高度:.2f}")
            if 圆角半径 > 0:
                info_lines.append(f"圆角半径: {圆角半径}px")
            if 旋转角度 != 0:
                info_lines.append(f"旋转: {旋转角度}°")
            if 实际羽化 > 0:
                info_lines.append(f"抗锯齿: {抗锯齿强度} (羽化{实际羽化:.1f}px)")
        
        elif 形状类型 == "圆形":
            mask = self.create_circle(w, h, 中心X, 中心Y, 半径, 实际羽化)
            info_lines.append(f"半径: {半径:.2f}")
            if 实际羽化 > 0:
                info_lines.append(f"抗锯齿: {抗锯齿强度} (羽化{实际羽化:.1f}px)")
        
        elif 形状类型 == "椭圆":
            mask = self.create_ellipse(w, h, 中心X, 中心Y, 长轴, 短轴, 旋转角度, 实际羽化)
            info_lines.append(f"长轴: {长轴:.2f}, 短轴: {短轴:.2f}")
            info_lines.append(f"旋转: {旋转角度}°")
            if 实际羽化 > 0:
                info_lines.append(f"抗锯齿: {抗锯齿强度} (羽化{实际羽化:.1f}px)")
        
        elif 形状类型 == "多边形":
            mask = self.create_polygon(w, h, 中心X, 中心Y, 半径, 边数, 旋转角度)
            info_lines.append(f"边数: {边数}, 半径: {半径:.2f}")
            info_lines.append(f"旋转: {旋转角度}°")
        
        elif 形状类型 == "星形":
            mask = self.create_star(w, h, 中心X, 中心Y, 半径, 内半径, 边数, 旋转角度)
            info_lines.append(f"外半径: {半径:.2f}, 内半径: {内半径:.2f}")
            info_lines.append(f"角数: {边数}, 旋转: {旋转角度}°")
        
        elif 形状类型 == "渐变":
            mask = self.create_gradient(w, h, 渐变类型, 渐变角度, 反转渐变)
            info_lines.append(f"渐变类型: {渐变类型}")
            info_lines.append(f"角度: {渐变角度}°")
            info_lines.append(f"反转: {'是' if 反转渐变 else '否'}")
        
        elif 形状类型 == "噪声":
            mask = self.create_noise(w, h, 噪声类型, 噪声强度, 噪声缩放)
            info_lines.append(f"噪声类型: {噪声类型}")
            info_lines.append(f"强度: {噪声强度:.2f}, 缩放: {噪声缩放:.1f}")
        
        elif 形状类型 == "棋盘":
            mask = self.create_checkerboard(w, h, 格子数X, 格子数Y)
            info_lines.append(f"格子数: {格子数X}×{格子数Y}")
        
        else:
            mask = np.zeros((h, w), dtype=np.float32)
            info_lines.append("未知形状类型")
        
        # 应用羽化（如果矩形/圆形/椭圆没有在生成时处理）
        if 羽化边缘 > 0 and 形状类型 not in ["矩形", "圆形", "椭圆"]:
            mask = self.apply_feather(mask, 羽化边缘)
            info_lines.append(f"羽化: {羽化边缘:.1f}px")
        
        # 处理输入遮罩操作
        if 输入遮罩 is not None and 操作模式 != "新建":
            # 转换输入遮罩为numpy
            if isinstance(输入遮罩, torch.Tensor):
                input_np = 输入遮罩.cpu().numpy()
                if len(input_np.shape) == 3:
                    input_np = input_np[0]  # 取第一个batch
            else:
                input_np = 输入遮罩
            
            # 确保尺寸匹配
            if input_np.shape != mask.shape:
                import cv2
                input_np = cv2.resize(input_np, (mask.shape[1], mask.shape[0]), interpolation=cv2.INTER_LINEAR)
            
            # 执行操作
            if 操作模式 == "叠加":
                mask = np.maximum(mask, input_np)
                info_lines.append("✓ 叠加模式: 与输入遮罩合并")
            elif 操作模式 == "相交":
                mask = np.minimum(mask, input_np)
                info_lines.append("✓ 相交模式: 仅保留重叠区域")
            elif 操作模式 == "差集":
                mask = np.maximum(input_np - mask, 0)
                info_lines.append("✓ 差集模式: 从输入中减去新形状")
            elif 操作模式 == "排除":
                # XOR操作
                mask = np.clip(mask + input_np - 2 * mask * input_np, 0, 1)
                info_lines.append("✓ 排除模式: 对称差集")
        
        # 反转
        if 反转遮罩:
            mask = 1.0 - mask
            info_lines.append("✓ 已反转")
        
        # 统计信息
        mask_area = float(np.sum(mask > 0.5))
        total_pixels = mask.size
        coverage = (mask_area / total_pixels) * 100 if total_pixels > 0 else 0
        mean_value = float(np.mean(mask))
        
        info_lines.append(f"\n=== 统计信息 ===")
        info_lines.append(f"遮罩面积: {mask_area:.0f} 像素")
        info_lines.append(f"覆盖率: {coverage:.2f}%")
        info_lines.append(f"平均值: {mean_value:.3f}")
        info_lines.append(f"中心位置: ({中心X:.2f}, {中心Y:.2f})")
        
        # 转换为torch张量
        result_mask = torch.from_numpy(mask).unsqueeze(0)
        info_text = "\n".join(info_lines)
        
        return (result_mask, info_text)


# ComfyUI节点注册
NODE_CLASS_MAPPINGS = {
    "MaskGeneratorNode": MaskGeneratorNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "MaskGeneratorNode": "🎨 遮罩生成器 (HAIGC)",
}

