"""
遮罩尺寸调整节点
作者: HAIGC Mask Development Team
功能: 专注于遮罩尺寸调整，支持多种插值方法和保持宽高比
"""

import torch
import numpy as np
import cv2

class MaskResizeNode:
    """遮罩尺寸调整节点 - 专注于尺寸调整功能"""
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "遮罩": ("MASK",),
                "目标宽度": ("INT", {"default": 512, "min": 8, "max": 8192, "step": 8, "display": "number"}),
                "目标高度": ("INT", {"default": 512, "min": 8, "max": 8192, "step": 8, "display": "number"}),
            },
            "optional": {
                "基准方式": (["遮罩区域", "画布尺寸"], {"default": "遮罩区域"}),
                "保持宽高比": ("BOOLEAN", {"default": True, "label_on": "是", "label_off": "否"}),
                "插值方法": (["最近邻", "双线性", "双三次", "兰索斯"], {"default": "双线性"}),
                "对齐方式": (["居中", "左上", "右上", "左下", "右下"], {"default": "居中"}),
                "边缘留白": ("INT", {"default": 0, "min": 0, "max": 200, "step": 1, "display": "number"}),
            }
        }
    
    RETURN_TYPES = ("MASK", "STRING", "INT", "INT")
    RETURN_NAMES = ("遮罩", "调整信息", "输出宽度", "输出高度")
    FUNCTION = "resize_mask"
    CATEGORY = "遮罩处理/HAIGC"
    
    # 中文到英文的映射
    RESIZE_METHOD_MAP = {
        "最近邻": cv2.INTER_NEAREST,
        "双线性": cv2.INTER_LINEAR,
        "双三次": cv2.INTER_CUBIC,
        "兰索斯": cv2.INTER_LANCZOS4
    }
    
    ALIGN_MAP = {
        "居中": "center",
        "左上": "top_left",
        "右上": "top_right",
        "左下": "bottom_left",
        "右下": "bottom_right"
    }
    
    def get_mask_bbox(self, mask_np, padding=0):
        """获取遮罩的有效区域边界框"""
        coords = np.where(mask_np > 0.5)
        if len(coords[0]) == 0:
            # 空遮罩，返回整个区域
            return 0, 0, mask_np.shape[1], mask_np.shape[0]
        
        y_min, y_max = coords[0].min(), coords[0].max()
        x_min, x_max = coords[1].min(), coords[1].max()
        
        # 添加padding
        h, w = mask_np.shape
        y_min = max(0, y_min - padding)
        y_max = min(h - 1, y_max + padding)
        x_min = max(0, x_min - padding)
        x_max = min(w - 1, x_max + padding)
        
        return x_min, y_min, x_max + 1, y_max + 1
    
    def resize_based_on_content(self, mask_np, target_width, target_height, keep_aspect_ratio, method, align, padding):
        """基于遮罩内容区域进行缩放"""
        h, w = mask_np.shape
        interpolation = self.RESIZE_METHOD_MAP.get(method, cv2.INTER_LINEAR)
        
        # 获取遮罩内容区域
        x_min, y_min, x_max, y_max = self.get_mask_bbox(mask_np, padding)
        content_w = x_max - x_min
        content_h = y_max - y_min
        
        # 裁剪出内容区域
        content_mask = mask_np[y_min:y_max, x_min:x_max]
        
        # 计算缩放比例
        if keep_aspect_ratio:
            scale = min(target_width / content_w, target_height / content_h)
            new_w = int(content_w * scale)
            new_h = int(content_h * scale)
        else:
            new_w = target_width
            new_h = target_height
            scale = min(new_w / content_w, new_h / content_h)
        
        # 缩放内容区域
        resized = cv2.resize(content_mask, (new_w, new_h), interpolation=interpolation)
        
        # 创建目标画布
        if keep_aspect_ratio and (new_w != target_width or new_h != target_height):
            canvas = np.zeros((target_height, target_width), dtype=np.float32)
            
            # 根据对齐方式放置
            align_en = self.ALIGN_MAP.get(align, "center")
            
            if align_en == "center":
                y_offset = (target_height - new_h) // 2
                x_offset = (target_width - new_w) // 2
            elif align_en == "top_left":
                y_offset = 0
                x_offset = 0
            elif align_en == "top_right":
                y_offset = 0
                x_offset = target_width - new_w
            elif align_en == "bottom_left":
                y_offset = target_height - new_h
                x_offset = 0
            elif align_en == "bottom_right":
                y_offset = target_height - new_h
                x_offset = target_width - new_w
            else:
                y_offset = (target_height - new_h) // 2
                x_offset = (target_width - new_w) // 2
            
            canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized
            return canvas, new_w, new_h, x_offset, y_offset, content_w, content_h, scale
        
        return resized, new_w, new_h, 0, 0, content_w, content_h, scale
    
    def resize_mask_from_center(self, mask_np, target_width, target_height, keep_aspect_ratio, method, align):
        """基于画布尺寸调整遮罩（保留原有行为）"""
        h, w = mask_np.shape
        
        # 转换插值方法
        interpolation = self.RESIZE_METHOD_MAP.get(method, cv2.INTER_LINEAR)
        
        if keep_aspect_ratio:
            # 计算缩放比例
            scale = min(target_width / w, target_height / h)
            new_w = int(w * scale)
            new_h = int(h * scale)
        else:
            new_w = target_width
            new_h = target_height
            scale = min(new_w / w, new_h / h)
        
        # 调整大小
        resized = cv2.resize(mask_np, (new_w, new_h), interpolation=interpolation)
        
        # 创建目标大小的画布
        if keep_aspect_ratio and (new_w != target_width or new_h != target_height):
            canvas = np.zeros((target_height, target_width), dtype=np.float32)
            
            # 根据对齐方式计算偏移
            align_en = self.ALIGN_MAP.get(align, "center")
            
            if align_en == "center":
                y_offset = (target_height - new_h) // 2
                x_offset = (target_width - new_w) // 2
            elif align_en == "top_left":
                y_offset = 0
                x_offset = 0
            elif align_en == "top_right":
                y_offset = 0
                x_offset = target_width - new_w
            elif align_en == "bottom_left":
                y_offset = target_height - new_h
                x_offset = 0
            elif align_en == "bottom_right":
                y_offset = target_height - new_h
                x_offset = target_width - new_w
            else:
                # 默认居中
                y_offset = (target_height - new_h) // 2
                x_offset = (target_width - new_w) // 2
            
            canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized
            return canvas, new_w, new_h, x_offset, y_offset, w, h, scale
        
        return resized, new_w, new_h, 0, 0, w, h, scale
    
    def resize_mask(self, 遮罩, 目标宽度, 目标高度, **kwargs):
        """主处理函数"""
        # 转换为numpy
        if isinstance(遮罩, torch.Tensor):
            mask_np = 遮罩.cpu().numpy()
        else:
            mask_np = 遮罩
        
        # 处理批次维度
        if len(mask_np.shape) == 3:
            mask_np = mask_np[0]
        
        original_shape = mask_np.shape
        基准方式 = kwargs.get('基准方式', '遮罩区域')
        保持宽高比 = kwargs.get('保持宽高比', True)
        插值方法 = kwargs.get('插值方法', '双线性')
        对齐方式 = kwargs.get('对齐方式', '居中')
        边缘留白 = kwargs.get('边缘留白', 0)
        
        # 构建信息
        info_lines = []
        info_lines.append(f"原始尺寸: {original_shape[1]}×{original_shape[0]}")
        info_lines.append(f"基准方式: {基准方式}")
        
        # 根据基准方式选择缩放方法
        if 基准方式 == "遮罩区域":
            result_np, actual_w, actual_h, offset_x, offset_y, content_w, content_h, scale = \
                self.resize_based_on_content(
                    mask_np,
                    目标宽度,
                    目标高度,
                    保持宽高比,
                    插值方法,
                    对齐方式,
                    边缘留白
                )
            info_lines.append(f"遮罩区域: {content_w}×{content_h}")
            if 边缘留白 > 0:
                info_lines.append(f"边缘留白: {边缘留白}px")
        else:
            result_np, actual_w, actual_h, offset_x, offset_y, content_w, content_h, scale = \
                self.resize_mask_from_center(
                    mask_np,
                    目标宽度,
                    目标高度,
                    保持宽高比,
                    插值方法,
                    对齐方式
                )
        
        info_lines.append(f"目标尺寸: {目标宽度}×{目标高度}")
        info_lines.append(f"实际缩放: {actual_w}×{actual_h}")
        info_lines.append(f"插值方法: {插值方法}")
        info_lines.append(f"缩放比例: {scale:.3f}x")
        
        if 保持宽高比:
            info_lines.append(f"对齐方式: {对齐方式}")
            if offset_x > 0 or offset_y > 0:
                info_lines.append(f"画布偏移: X={offset_x}, Y={offset_y}")
        else:
            info_lines.append(f"保持宽高比: 否（拉伸）")
        
        # 统计信息
        mask_area = float(np.sum(result_np > 0.5))
        total_pixels = result_np.size
        coverage = (mask_area / total_pixels) * 100 if total_pixels > 0 else 0
        
        info_lines.append(f"\n=== 统计信息 ===")
        info_lines.append(f"遮罩面积: {mask_area:.0f} 像素")
        info_lines.append(f"覆盖率: {coverage:.2f}%")
        info_lines.append(f"最终尺寸: {result_np.shape[1]}×{result_np.shape[0]}")
        
        # 转换回torch张量
        result_mask = torch.from_numpy(result_np).unsqueeze(0)
        info_text = "\n".join(info_lines)
        
        return (result_mask, info_text, result_np.shape[1], result_np.shape[0])


# ComfyUI节点注册
NODE_CLASS_MAPPINGS = {
    "MaskResizeNode": MaskResizeNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "MaskResizeNode": "📐 遮罩尺寸调整 (HAIGC)",
}

