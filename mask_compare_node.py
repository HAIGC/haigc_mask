"""
遮罩比较节点 - 比较两个遮罩的差异
作者: HAIGC Mask Development Team
功能: 提供多种遮罩比较算法
"""

import torch
import numpy as np
import cv2


class MaskCompareNode:
    """遮罩比较节点 - 比较两个遮罩的差异"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "遮罩A": ("MASK",),
                "遮罩B": ("MASK",),
            },
            "optional": {
                "比较模式": (["差异度", "相似度", "IoU交并比", "Dice系数"], 
                                   {"default": "差异度"}),
            }
        }
    
    RETURN_TYPES = ("MASK", "FLOAT", "STRING")
    RETURN_NAMES = ("差异遮罩", "得分", "比较信息")
    FUNCTION = "compare_masks"
    CATEGORY = "遮罩处理/HAIGC"
    
    # 中文到英文的映射
    COMPARISON_MODE_MAP = {
        "差异度": "difference",
        "相似度": "similarity",
        "IoU交并比": "iou",
        "Dice系数": "dice"
    }
    
    def compare_masks(self, 遮罩A, 遮罩B, 比较模式="差异度"):
        """比较两个遮罩"""
        # 转换中文模式
        if 比较模式 in self.COMPARISON_MODE_MAP:
            comparison_mode = self.COMPARISON_MODE_MAP[比较模式]
        else:
            comparison_mode = 比较模式
            
        # 转换为numpy
        if isinstance(遮罩A, torch.Tensor):
            mask_a_np = 遮罩A.cpu().numpy()
        else:
            mask_a_np = 遮罩A
        
        if isinstance(遮罩B, torch.Tensor):
            mask_b_np = 遮罩B.cpu().numpy()
        else:
            mask_b_np = 遮罩B
        
        # 处理批次维度
        if len(mask_a_np.shape) == 3:
            mask_a_np = mask_a_np[0]
        if len(mask_b_np.shape) == 3:
            mask_b_np = mask_b_np[0]
        
        # 确保尺寸相同
        if mask_a_np.shape != mask_b_np.shape:
            # 调整mask_b到mask_a的尺寸
            mask_b_np = cv2.resize(mask_b_np, (mask_a_np.shape[1], mask_a_np.shape[0]))
        
        info_lines = []
        
        if comparison_mode == "difference":
            # 差异遮罩
            diff_mask = np.abs(mask_a_np - mask_b_np)
            score = float(np.mean(diff_mask))
            info_lines.append(f"差异度: {score:.4f} (0=完全相同, 1=完全不同)")
            
        elif comparison_mode == "similarity":
            # 相似度
            similarity = 1.0 - np.mean(np.abs(mask_a_np - mask_b_np))
            diff_mask = np.abs(mask_a_np - mask_b_np)
            score = float(similarity)
            info_lines.append(f"相似度: {score:.4f} (0=完全不同, 1=完全相同)")
            
        elif comparison_mode == "iou":
            # IoU (Intersection over Union)
            intersection = np.logical_and(mask_a_np > 0.5, mask_b_np > 0.5)
            union = np.logical_or(mask_a_np > 0.5, mask_b_np > 0.5)
            iou = np.sum(intersection) / (np.sum(union) + 1e-8)
            diff_mask = np.abs(mask_a_np - mask_b_np)
            score = float(iou)
            info_lines.append(f"IoU: {score:.4f}")
            info_lines.append(f"交集: {np.sum(intersection)}")
            info_lines.append(f"并集: {np.sum(union)}")
            
        elif comparison_mode == "dice":
            # Dice系数
            intersection = np.logical_and(mask_a_np > 0.5, mask_b_np > 0.5)
            dice = (2.0 * np.sum(intersection)) / (np.sum(mask_a_np > 0.5) + np.sum(mask_b_np > 0.5) + 1e-8)
            diff_mask = np.abs(mask_a_np - mask_b_np)
            score = float(dice)
            info_lines.append(f"Dice系数: {score:.4f}")
        
        info_lines.append(f"\nMask A 面积: {np.sum(mask_a_np > 0.5):.0f}")
        info_lines.append(f"Mask B 面积: {np.sum(mask_b_np > 0.5):.0f}")
        
        result_mask = torch.from_numpy(diff_mask).unsqueeze(0)
        info_text = "\n".join(info_lines)
        
        return (result_mask, score, info_text)


# 节点注册
NODE_CLASS_MAPPINGS = {
    "MaskCompareNode": MaskCompareNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "MaskCompareNode": "⚖️ 遮罩比较节点 (HAIGC)",
}

