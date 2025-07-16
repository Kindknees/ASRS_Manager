import itertools
from bin import Bin
from item import Item
import utils

class BEST_FIT:
    """
    Best Fit (Offline) - 專為垂直堆疊設計。
    主要考慮高度限制，但同時檢查長寬是否符合櫃子底面積。
    """

    @staticmethod
    def best_fit(items:list, bin_dimensions):
        """
        使用 Best Fit 演算法進行 3D Bin Packing。

        :param items: 物品清單 (list of Item objects)
        :param bin_dimensions: 貨櫃尺寸 (width, height, depth)
        :return: (已使用的貨櫃清單, 未能放入的物品清單)
        """
        bins = []
        unplaced_items = []
        bin_width, bin_height, bin_depth, bin_min_adjust_length = bin_dimensions

        items.sort(key=lambda i: i.height, reverse=True)

        for item in items:
            optimal_orientation = utils.get_optimal_dimension(item, bin_dimensions)
            
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
                        adjusted_item_height = utils.get_adjusted_height(item.placed_dimensions[1], bin.min_adjust_length)
                        resulting_height = position[1] + adjusted_item_height

                        if resulting_height < min_resulting_height:
                            min_resulting_height = resulting_height
                            best_position = position
                            best_bin = bin
            
            # if best bin is found, put the item to the bin
            if best_bin:
                best_bin.place_item(item, best_position)
            # else: open a new bin
            else:
                new_bin = Bin(bin_width, bin_height, bin_depth, bin_min_adjust_length)
                # 放在新貨櫃的 (0, 0, 0) 位置
                if new_bin.can_place(item, (0, 0, 0)):
                    new_bin.place_item(item, (0, 0, 0))
                    bins.append(new_bin)
                else:
                    unplaced_items.append(item)

        return bins, unplaced_items