from bin import Bin
class FIRST_FIT:
    """
    First Fit (Online) - 專為垂直堆疊設計。

    主要考慮高度限制，但同時檢查長寬是否符合櫃子底面積。
    優先使用物品較短的邊作為高度。

    :param current_bins: 當前已使用的貨櫃(堆疊)清單
    :param item_to_place: 一件剛到達的、需要被放置的物品
    :param bin_width: 櫃子的寬度限制
    :param bin_depth: 櫃子的深度限制
    :param bin_height: 櫃子的總高度限制
    :return: (bool): True 表示放置成功, False 表示失敗
    """
    @staticmethod
    def get_rotations_for_stacking(item):
        """
        為垂直堆疊產生旋轉方式，並按高度(h)從低到高排序。
        產生的格式為 (w, h, d)
        """
        if item.rotation == 0:
            # 如果不允許旋轉，只有一種方式
            yield (item.width, item.height, item.depth)
            return

        # 將三邊長和其對應的另外兩邊打包
        # 格式為 (height, other_dim1, other_dim2)
        rotations = [
            (item.height, item.width, item.depth),
            (item.width, item.height, item.depth),
            (item.depth, item.height, item.width)
        ]

        # 依照高度(第一個元素)排序
        rotations.sort()

        for h, d1, d2 in rotations:
            # 對於每個高度，它的底面積有兩種擺法 (d1 x d2) 或 (d2 x d1)
            # 產生的格式是 (width, height, depth)
            yield (d1, h, d2)
            if d1 != d2: # 如果長寬不一樣，才需要交換產生第二種
                yield (d2, h, d1)
    
    @staticmethod            
    def first_fit_1D_stacking(current_bins, item_to_place, bin_dimensions):
        bin_width, bin_depth, bin_height, bin_min_adjust_length = bin_dimensions
        # 依序檢查現有貨櫃 (每個貨櫃代表一個堆疊)
        for bin_obj in current_bins:
            current_stacked_height = bin_obj.get_current_height()
            for rotation in FIRST_FIT.get_rotations_for_stacking(item_to_place):
                w, h, d = rotation
                item_to_place.placed_dimensions = (w, h, d)
                if (w <= bin_obj.width and d <= bin_obj.depth):
                    if current_stacked_height + h <= bin_obj.height:
                        position = (0, current_stacked_height, 0)
                        bin_obj.place_item(item_to_place, position)
                        return True

        # 檢查物品本身是否能裝進一個空的貨櫃
        for rotation in FIRST_FIT.get_rotations_for_stacking(item_to_place):
            w, h, d = rotation
            item_to_place.placed_dimensions = (w, h, d)

            # 檢查長寬和高度是否符合一個全新的空櫃子
            if (w <= bin_width and d <= bin_depth) and (h <= bin_height):
                new_bin = Bin(width=bin_width, height=bin_height, depth=bin_depth, min_adjust_length=5)
                new_bin.place_item(item_to_place, (0, 0, 0))
                current_bins.append(new_bin)
                return True # 放置成功

        # 如果連新的空貨櫃都放不下（物品尺寸過大）
        item_to_place.position = None
        return False # 放置失敗