from bin import Bin
import utils

class FIRST_FIT:
    """
    First Fit (Online) - 專為垂直堆疊設計。

    主要考慮高度限制，但同時檢查長寬是否符合櫃子底面積。
    優先使用物品較短的邊作為高度。
    """
    
    @staticmethod            
    def first_fit_1D_stacking(current_bins, item_to_place, bin_dimensions):
        bin_width, bin_height, bin_depth, bin_min_adjust_length = bin_dimensions
        item_dimension = utils.get_optimal_dimension(item_to_place, bin_dimensions)
        if item_dimension is None:
                return False
        # 依序檢查現有貨櫃 (每個貨櫃代表一個堆疊)
        for bin_obj in current_bins:
            current_stacked_height = bin_obj.get_current_height()
            w, h, d = item_dimension
            item_to_place.placed_dimensions = (w, h, d)
            adjusted_height = utils.get_adjusted_height(h, bin_min_adjust_length)
            if current_stacked_height + adjusted_height <= bin_obj.height:
                position = (0, current_stacked_height, 0)
                bin_obj.place_item(item_to_place, position)
                return True

        # put the item to a new bin
        w, h, d = item_dimension

        adjusted_height = utils.get_adjusted_height(h, bin_min_adjust_length)

        # 檢查長寬和高度是否符合一個全新的空櫃子
        if (adjusted_height <= bin_height):
            new_bin = Bin(width=bin_width, height=bin_height, depth=bin_depth, min_adjust_length=bin_min_adjust_length)
            new_bin.place_item(item_to_place, (0, 0, 0))
            current_bins.append(new_bin)
            return True
            
        # failed to place item
        item_to_place.position = None
        return False