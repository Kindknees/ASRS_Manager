import math
import itertools

def get_adjusted_height(item_height_value, min_adjust_length):
    if min_adjust_length <= 0:
        return item_height_value
    return math.ceil(item_height_value / min_adjust_length) * min_adjust_length

def get_optimal_dimension(item, bin_dimensions):
        """
        return: 最佳的 (width, height, depth) 元組，如果無法放入則返回 None。
        """
        dims = [item.width, item.height, item.depth]
        bin_width, bin_height, bin_depth = bin_dimensions[:3]
        
        if item.rotation == 0:
            # 不允許旋轉，直接檢查是否符合底面積
            if (dims[0] <= bin_width and dims[2] <= bin_depth):
                return tuple(dims)
            
            elif(dims[2] <= bin_width and dims[0] <= bin_depth):
                new_dims = [dims[2], dims[1], dims[0]]
                return tuple(new_dims)
            else:
                return None

        # 產生所有可能的方向 (w, h, d)
        possible_orientations = list(set(itertools.permutations(dims)))
        
        valid_orientations = []
        for w, h, d in possible_orientations:
            # 檢查長寬是否符合 (允許底部90度旋轉)
            if (w <= bin_width and h <= bin_height and d <= bin_depth):
               valid_orientations.append((w, h, d))
            elif(d <= bin_width and h <= bin_height and w <= bin_depth):
                valid_orientations.append((d, h, w))
        
        if not valid_orientations:
            return None # 沒有任何方向可以放入貨櫃底部
            
        valid_orientations.sort(key=lambda o: o[1])
        return valid_orientations[0]