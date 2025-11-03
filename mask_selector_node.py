"""
多遮罩选择器节点
专门用于检测、排序和选择多个遮罩
"""

import torch
import numpy as np
import cv2

class MultiMaskSelectorNode:
    """多遮罩选择器 - 检测和选择多个遮罩"""
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "遮罩": ("MASK",),
                "排序方向": (["从上到下", "从下到上", "从左到右", "从右到左", "面积大到小", "面积小到大"], 
                          {"default": "从上到下"}),
                "选择模式": (["单个遮罩", "所有遮罩", "前N个遮罩"], {"default": "单个遮罩"}),
            },
            "optional": {
                "遮罩索引": ("INT", {"default": 0, "min": 0, "max": 99, "step": 1, "display": "number"}),
                "选择数量": ("INT", {"default": 3, "min": 1, "max": 50, "step": 1, "display": "number"}),
                "最小面积": ("INT", {"default": 10, "min": 1, "max": 10000, "step": 1, "display": "number"}),
            }
        }
    
    RETURN_TYPES = ("MASK", "STRING", "INT", "STRING")
    RETURN_NAMES = ("遮罩", "详细信息", "遮罩总数", "遮罩列表")
    FUNCTION = "select_masks"
    CATEGORY = "遮罩处理/HAIGC"
    
    # 排序方向映射
    SORT_MAP = {
        "从上到下": "top_to_bottom",
        "从下到上": "bottom_to_top",
        "从左到右": "left_to_right",
        "从右到左": "right_to_left",
        "面积大到小": "area_large_to_small",
        "面积小到大": "area_small_to_large"
    }
    
    def detect_and_sort_masks(self, mask_np, sort_direction, min_area=10):
        """检测多个遮罩并排序"""
        # 转换排序方向
        if sort_direction in self.SORT_MAP:
            sort_direction = self.SORT_MAP[sort_direction]
        
        # 使用连通组件标记
        binary_mask = (mask_np > 0.5).astype(np.uint8)
        num_features, labeled = cv2.connectedComponents(binary_mask)
        
        if num_features <= 1:  # 0 是背景，1 表示只有背景
            return [], []
        
        masks_info = []
        for i in range(1, num_features):  # 从1开始，跳过背景(0)
            mask_region = (labeled == i).astype(np.float32)
            
            # 计算边界框和中心
            coords = np.where(labeled == i)
            if len(coords[0]) == 0:
                continue
            
            y_min, y_max = coords[0].min(), coords[0].max()
            x_min, x_max = coords[1].min(), coords[1].max()
            center_y = (y_min + y_max) / 2
            center_x = (x_min + x_max) / 2
            area = np.sum(mask_region)
            
            # 过滤太小的区域
            if area < min_area:
                continue
            
            masks_info.append({
                'mask': mask_region,
                'center_y': center_y,
                'center_x': center_x,
                'y_min': y_min,
                'y_max': y_max,
                'x_min': x_min,
                'x_max': x_max,
                'area': area,
                'width': x_max - x_min + 1,
                'height': y_max - y_min + 1,
                'bbox': (int(x_min), int(y_min), int(x_max), int(y_max))
            })
        
        # 排序
        if sort_direction == "top_to_bottom":
            masks_info.sort(key=lambda x: x['center_y'])
        elif sort_direction == "bottom_to_top":
            masks_info.sort(key=lambda x: -x['center_y'])
        elif sort_direction == "left_to_right":
            masks_info.sort(key=lambda x: x['center_x'])
        elif sort_direction == "right_to_left":
            masks_info.sort(key=lambda x: -x['center_x'])
        elif sort_direction == "area_large_to_small":
            masks_info.sort(key=lambda x: -x['area'])
        elif sort_direction == "area_small_to_large":
            masks_info.sort(key=lambda x: x['area'])
        
        return masks_info, labeled
    
    def select_masks(self, 遮罩, 排序方向, 选择模式, 遮罩索引=0, 选择数量=3, 最小面积=10):
        """选择遮罩"""
        # 转换为numpy
        if isinstance(遮罩, torch.Tensor):
            mask_np = 遮罩.cpu().numpy()
        else:
            mask_np = 遮罩
        
        # 处理批次维度
        if len(mask_np.shape) == 3:
            mask_np = mask_np[0]
        
        # 检测和排序遮罩
        masks_info, labeled = self.detect_and_sort_masks(mask_np, 排序方向, 最小面积)
        
        mask_count = len(masks_info)
        info_lines = []
        info_lines.append(f"检测到 {mask_count} 个遮罩")
        info_lines.append(f"排序方式: {排序方向}")
        info_lines.append(f"最小面积过滤: {最小面积} 像素")
        
        # 根据选择模式处理
        if mask_count == 0:
            # 没有检测到遮罩，返回空遮罩
            result_mask = np.zeros_like(mask_np)
            info_lines.append("⚠ 未检测到符合条件的遮罩")
            mask_list = "无"
        
        elif 选择模式 == "单个遮罩":
            # 选择单个遮罩
            if 遮罩索引 < mask_count:
                result_mask = masks_info[遮罩索引]['mask']
                selected = masks_info[遮罩索引]
                info_lines.append(f"\n【选中遮罩 #{遮罩索引}】")
                info_lines.append(f"  位置: ({selected['x_min']}, {selected['y_min']}) 到 ({selected['x_max']}, {selected['y_max']})")
                info_lines.append(f"  尺寸: {selected['width']} x {selected['height']}")
                info_lines.append(f"  面积: {selected['area']:.0f} 像素")
                info_lines.append(f"  中心: ({selected['center_x']:.1f}, {selected['center_y']:.1f})")
                mask_list = f"遮罩 #{遮罩索引}"
            else:
                result_mask = masks_info[0]['mask']
                info_lines.append(f"⚠ 索引 {遮罩索引} 超出范围，使用遮罩 #0")
                mask_list = "遮罩 #0 (默认)"
        
        elif 选择模式 == "所有遮罩":
            # 合并所有遮罩
            result_mask = np.zeros_like(mask_np)
            for idx, mask_info in enumerate(masks_info):
                result_mask = np.maximum(result_mask, mask_info['mask'])
            info_lines.append(f"\n合并了所有 {mask_count} 个遮罩")
            mask_list = f"全部 {mask_count} 个遮罩"
        
        elif 选择模式 == "前N个遮罩":
            # 选择前N个遮罩
            actual_count = min(选择数量, mask_count)
            result_mask = np.zeros_like(mask_np)
            for idx in range(actual_count):
                result_mask = np.maximum(result_mask, masks_info[idx]['mask'])
            info_lines.append(f"\n合并了前 {actual_count} 个遮罩")
            mask_list = f"前 {actual_count} 个遮罩"
        
        # 生成遮罩列表信息
        list_lines = [f"共 {mask_count} 个遮罩:\n"]
        for idx, m_info in enumerate(masks_info):
            list_lines.append(
                f"#{idx}: 位置({m_info['x_min']},{m_info['y_min']}) "
                f"尺寸{m_info['width']}x{m_info['height']} "
                f"面积{m_info['area']:.0f}"
            )
        
        # 转换回torch张量
        result_tensor = torch.from_numpy(result_mask).unsqueeze(0)
        
        info_text = "\n".join(info_lines)
        list_text = "\n".join(list_lines)
        
        return (result_tensor, info_text, mask_count, list_text)


# 节点注册
NODE_CLASS_MAPPINGS = {
    "MultiMaskSelectorNode": MultiMaskSelectorNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "MultiMaskSelectorNode": "🎯 多遮罩选择器 (HAIGC)",
}

