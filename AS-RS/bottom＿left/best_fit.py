import itertools
from bin import Bin
from item import Item

class BEST_FIT:
    """
    Best Fit (Offline) - 專為垂直堆疊設計。
    主要考慮高度限制，但同時檢查長寬是否符合櫃子底面積。
    """

    @staticmethod
    def best_fit(items, bin_dimensions):
        """
        使用 Best Fit 演算法進行 3D Bin Packing。

        :param items: 物品清單 (list of Item objects)
        :param bin_dimensions: 貨櫃尺寸 (width, height, depth)
        :return: (已使用的貨櫃清單, 未能放入的物品清單)
        """
        bins = []
        unplaced_items = []
        bin_width, bin_height, bin_depth, bin_min_adjust_length = bin_dimensions

        # 預處理 1：將物品按面積或最大邊長排序，有利於先放大家具
        items.sort(key=lambda i: i.height, reverse=True)

        for item in items:
            # 預處理 2：為物品決定最佳擺放方向
            optimal_orientation = BEST_FIT._determine_optimal_orientation(item, bin_dimensions)
            
            if optimal_orientation is None:
                unplaced_items.append(item)
                continue
            
            item.placed_dimensions = optimal_orientation

            # 開始為這個已確定方向的物品尋找最佳位置
            best_bin = None
            best_position = None
            # 評分標準：尋找能使物品放置後，貨櫃總高度最低的方案
            min_resulting_height = float('inf')

            for bin in bins:
                for position in bin.get_possible_positions(item):
                    if bin.can_place(item, position):
                        # 計算如果放在這裡，新的總高度會是多少
                        resulting_height = position[1] + item.placed_dimensions[1]
                        if resulting_height < min_resulting_height:
                            min_resulting_height = resulting_height
                            best_position = position
                            best_bin = bin
            
            # 如果在所有現有貨櫃中找到了最佳位置
            if best_bin:
                best_bin.place_item(item, best_position)
            else:
                new_bin = Bin(bin_width, bin_height, bin_depth, bin_min_adjust_length)
                # 放在新貨櫃的 (0, 0, 0) 位置
                new_bin.place_item(item, (0, 0, 0))
                bins.append(new_bin)

        return bins, unplaced_items
    
    @staticmethod
    def get_rotations(item):
        """
        如果允許旋轉，生成物品所有可能的旋轉方向 (長, 寬, 高)。
        """
        if item.rotation == 0:
            yield (item.width, item.height, item.depth)
            return

        # 產生長寬高的所有排列組合，共 3! = 6 種
        for w, h, d in set(itertools.permutations([item.width, item.height, item.depth])):
            yield (w, h, d)
    
    @staticmethod
    def _determine_optimal_orientation(item, bin_dimensions):
        """
        根據「高度最小化」和「符合底面積」的原則，決定物品的最佳方向。
        :return: 最佳的 (width, height, depth) 元組，如果無法放入則返回 None。
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
            # 檢查底面積是否符合 (允許底部90度旋轉)
            if (w <= bin_width and h <= bin_height and d <= bin_depth):
               valid_orientations.append((w, h, d))
            elif(d <= bin_width and h <= bin_height and w <= bin_depth):
                valid_orientations.append((d, h, w))
        
        if not valid_orientations:
            return None # 沒有任何方向可以放入貨櫃底部
            
        # 從所有有效的方向中，選擇高度 h 最小的那個
        valid_orientations.sort(key=lambda o: o[1])
        return valid_orientations[0]