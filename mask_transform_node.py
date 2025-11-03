"""
遮罩变换节点
作者: HAIGC Mask Development Team
功能: 尺寸调整、旋转、偏移、裁剪等变换操作
"""

import torch
import numpy as np
import cv2

class MaskTransformNode:
    """遮罩变换节点 - 专注于几何变换操作"""
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "遮罩": ("MASK",),
            },
            "optional": {
                # === 尺寸调整 ===
                "启用尺寸调整": ("BOOLEAN", {"default": False, "label_on": "开启", "label_off": "关闭"}),
                "基准方式": (["遮罩区域", "画布尺寸"], {"default": "遮罩区域"}),
                "目标宽度": ("INT", {"default": 512, "min": 8, "max": 8192, "step": 8, "display": "number"}),
                "目标高度": ("INT", {"default": 512, "min": 8, "max": 8192, "step": 8, "display": "number"}),
                "保持宽高比": ("BOOLEAN", {"default": True, "label_on": "是", "label_off": "否"}),
                "插值方法": (["最近邻", "双线性", "双三次", "兰索斯"], {"default": "双线性"}),
                "边缘留白": ("INT", {"default": 0, "min": 0, "max": 200, "step": 1, "display": "number"}),
                
                # === 旋转 ===
                "启用旋转": ("BOOLEAN", {"default": False, "label_on": "开启", "label_off": "关闭"}),
                "旋转角度": ("FLOAT", {"default": 0.0, "min": -360.0, "max": 360.0, "step": 1.0, "display": "number"}),
                
                # === 位置偏移 ===
                "启用偏移": ("BOOLEAN", {"default": False, "label_on": "开启", "label_off": "关闭"}),
                "X偏移": ("INT", {"default": 0, "min": -4096, "max": 4096, "step": 1, "display": "number"}),
                "Y偏移": ("INT", {"default": 0, "min": -4096, "max": 4096, "step": 1, "display": "number"}),
                
                # === 裁剪到边界框 ===
                "裁剪到边界框": ("BOOLEAN", {"default": False, "label_on": "是", "label_off": "否"}),
                "边界框填充": ("INT", {"default": 0, "min": 0, "max": 500, "step": 1, "display": "number"}),
            }
        }
    
    RETURN_TYPES = ("MASK", "STRING")
    RETURN_NAMES = ("遮罩", "变换信息")
    FUNCTION = "transform_mask"
    CATEGORY = "遮罩处理/HAIGC"
    
    # 中文到英文的映射
    RESIZE_METHOD_MAP = {
        "最近邻": "nearest",
        "双线性": "bilinear",
        "双三次": "bicubic",
        "兰索斯": "lanczos"
    }
    
    def get_mask_bbox(self, mask_np, padding=0):
        """获取遮罩的有效区域边界框"""
        coords = np.where(mask_np > 0.5)
        if len(coords[0]) == 0:
            return 0, 0, mask_np.shape[1], mask_np.shape[0]
        
        y_min, y_max = coords[0].min(), coords[0].max()
        x_min, x_max = coords[1].min(), coords[1].max()
        
        h, w = mask_np.shape
        y_min = max(0, y_min - padding)
        y_max = min(h - 1, y_max + padding)
        x_min = max(0, x_min - padding)
        x_max = min(w - 1, x_max + padding)
        
        return x_min, y_min, x_max + 1, y_max + 1
    
    def resize_based_on_content(self, mask_np, target_width, target_height, keep_aspect_ratio, method, padding):
        """基于遮罩内容区域进行缩放"""
        if method in self.RESIZE_METHOD_MAP:
            method = self.RESIZE_METHOD_MAP[method]
        
        if method == "nearest":
            interpolation = cv2.INTER_NEAREST
        elif method == "bilinear":
            interpolation = cv2.INTER_LINEAR
        elif method == "bicubic":
            interpolation = cv2.INTER_CUBIC
        elif method == "lanczos":
            interpolation = cv2.INTER_LANCZOS4
        else:
            interpolation = cv2.INTER_LINEAR
        
        # 获取内容区域
        x_min, y_min, x_max, y_max = self.get_mask_bbox(mask_np, padding)
        content_w = x_max - x_min
        content_h = y_max - y_min
        
        # 裁剪内容
        content_mask = mask_np[y_min:y_max, x_min:x_max]
        
        # 计算缩放
        if keep_aspect_ratio:
            scale = min(target_width / content_w, target_height / content_h)
            new_w = int(content_w * scale)
            new_h = int(content_h * scale)
        else:
            new_w = target_width
            new_h = target_height
        
        # 缩放
        resized = cv2.resize(content_mask, (new_w, new_h), interpolation=interpolation)
        
        # 放置到画布
        if keep_aspect_ratio and (new_w != target_width or new_h != target_height):
            canvas = np.zeros((target_height, target_width), dtype=np.float32)
            y_offset = (target_height - new_h) // 2
            x_offset = (target_width - new_w) // 2
            canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized
            return canvas
        
        return resized
    
    def resize_mask_from_center(self, mask_np, target_width, target_height, keep_aspect_ratio, method):
        """基于画布尺寸调整遮罩"""
        if method in self.RESIZE_METHOD_MAP:
            method = self.RESIZE_METHOD_MAP[method]
            
        h, w = mask_np.shape
        
        if keep_aspect_ratio:
            scale = min(target_width / w, target_height / h)
            new_w = int(w * scale)
            new_h = int(h * scale)
        else:
            new_w = target_width
            new_h = target_height
        
        if method == "nearest":
            interpolation = cv2.INTER_NEAREST
        elif method == "bilinear":
            interpolation = cv2.INTER_LINEAR
        elif method == "bicubic":
            interpolation = cv2.INTER_CUBIC
        elif method == "lanczos":
            interpolation = cv2.INTER_LANCZOS4
        else:
            interpolation = cv2.INTER_LINEAR
        
        resized = cv2.resize(mask_np, (new_w, new_h), interpolation=interpolation)
        
        if keep_aspect_ratio:
            canvas = np.zeros((target_height, target_width), dtype=np.float32)
            y_offset = (target_height - new_h) // 2
            x_offset = (target_width - new_w) // 2
            canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized
            return canvas
        
        return resized
    
    def rotate_mask(self, mask_np, angle):
        """旋转遮罩"""
        if angle == 0:
            return mask_np
        
        h, w = mask_np.shape
        center = (w / 2, h / 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(mask_np, M, (w, h))
        return rotated
    
    def offset_mask(self, mask_np, offset_x, offset_y):
        """偏移遮罩位置"""
        if offset_x == 0 and offset_y == 0:
            return mask_np
        
        h, w = mask_np.shape
        M = np.float32([[1, 0, offset_x], [0, 1, offset_y]])
        shifted = cv2.warpAffine(mask_np, M, (w, h))
        return shifted
    
    def crop_to_bounding_box(self, mask_np, padding):
        """裁剪到边界框"""
        coords = np.where(mask_np > 0.5)
        if len(coords[0]) == 0:
            return mask_np
        
        y_min, y_max = coords[0].min(), coords[0].max()
        x_min, x_max = coords[1].min(), coords[1].max()
        
        # 添加填充
        h, w = mask_np.shape
        y_min = max(0, y_min - padding)
        y_max = min(h, y_max + padding + 1)
        x_min = max(0, x_min - padding)
        x_max = min(w, x_max + padding + 1)
        
        return mask_np[y_min:y_max, x_min:x_max]
    
    def transform_mask(self, 遮罩, **kwargs):
        """主处理函数"""
        # 转换为numpy
        if isinstance(遮罩, torch.Tensor):
            mask_np = 遮罩.cpu().numpy()
        else:
            mask_np = 遮罩
        
        # 处理批次维度
        if len(mask_np.shape) == 3:
            mask_np = mask_np[0]
        
        info_lines = []
        original_shape = mask_np.shape
        
        # === 1. 尺寸调整 ===
        if kwargs.get('启用尺寸调整', False):
            基准方式 = kwargs.get('基准方式', '遮罩区域')
            边缘留白 = kwargs.get('边缘留白', 0)
            
            if 基准方式 == "遮罩区域":
                mask_np = self.resize_based_on_content(
                    mask_np,
                    kwargs.get('目标宽度', 512),
                    kwargs.get('目标高度', 512),
                    kwargs.get('保持宽高比', True),
                    kwargs.get('插值方法', '双线性'),
                    边缘留白
                )
            else:
                mask_np = self.resize_mask_from_center(
                    mask_np,
                    kwargs.get('目标宽度', 512),
                    kwargs.get('目标高度', 512),
                    kwargs.get('保持宽高比', True),
                    kwargs.get('插值方法', '双线性')
                )
            info_lines.append(f"✓ 尺寸调整({基准方式}): {original_shape} → {mask_np.shape}")
        
        # === 2. 旋转 ===
        if kwargs.get('启用旋转', False):
            angle = kwargs.get('旋转角度', 0.0)
            if angle != 0:
                mask_np = self.rotate_mask(mask_np, angle)
                info_lines.append(f"✓ 旋转: {angle}°")
        
        # === 3. 位置偏移 ===
        if kwargs.get('启用偏移', False):
            offset_x = kwargs.get('X偏移', 0)
            offset_y = kwargs.get('Y偏移', 0)
            if offset_x != 0 or offset_y != 0:
                mask_np = self.offset_mask(mask_np, offset_x, offset_y)
                info_lines.append(f"✓ 位置偏移: X={offset_x}, Y={offset_y}")
        
        # === 4. 裁剪到边界框 ===
        if kwargs.get('裁剪到边界框', False):
            padding = kwargs.get('边界框填充', 0)
            old_shape = mask_np.shape
            mask_np = self.crop_to_bounding_box(mask_np, padding)
            info_lines.append(f"✓ 裁剪到边界框: {old_shape} → {mask_np.shape} (填充={padding})")
        
        # 统计信息
        mask_area = float(np.sum(mask_np > 0.5))
        total_pixels = mask_np.size
        coverage = (mask_area / total_pixels) * 100 if total_pixels > 0 else 0
        
        info_lines.append(f"\n=== 统计信息 ===")
        info_lines.append(f"最终尺寸: {mask_np.shape}")
        info_lines.append(f"遮罩面积: {mask_area:.0f} 像素")
        info_lines.append(f"覆盖率: {coverage:.2f}%")
        
        # 转换回torch张量
        result_mask = torch.from_numpy(mask_np).unsqueeze(0)
        info_text = "\n".join(info_lines) if info_lines else "未进行任何变换"
        
        return (result_mask, info_text)


# ComfyUI节点注册
NODE_CLASS_MAPPINGS = {
    "MaskTransformNode": MaskTransformNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "MaskTransformNode": "🔄 遮罩变换 (HAIGC)",
}

