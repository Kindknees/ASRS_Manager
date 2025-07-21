import itertools
from bin import Bin
from item import Item
import utils

# 應該更正成找剩餘空間最少的，然後放進去那個櫃子？
def best_fit(items:list, all_bins, bin_dimensions, offline_priority=None):
    """
    Applies the offline Best Fit algorithm to pack 3D items into bins.

    This method first sorts items by height. For each item, if it is rotatable, it determines
    an optimal, height-minimized orientation. It then searches all existing
    bins to find the placement that results in the lowest new total height.
    If no suitable space is found in existing bins, a new bin is created.

    :param items: A list of Item objects to be packed.
    :param bin_dimensions: A tuple representing the dimensions
                            (width, height, depth, min_adjust_length) of the bins.
    :return: list of unplaced Item objects).
    """
    unplaced_items = []
    _, bin_height, _, _ = bin_dimensions
    # rotate items to height-minimized orientation
    for item in items:
        optimal_orientation = utils.get_optimal_dimension(item, bin_dimensions)
        
        if optimal_orientation is None:
            unplaced_items.append(item)
            continue  
        item.placed_dimensions = optimal_orientation
    # print (f"original items: {[i.id for i in items[:10]]}")
    # sort items by height in descending order after rotation
    items.sort(key=lambda i: i.placed_dimensions[1], reverse=True)
    # print (f"sorted items: {[i.id for i in items[:10]]}")

    #best fit algorithm start
    for item in items:
        best_bin_id = None
        best_position = None
        # scoring: # find the bin that results in the lowest new total height
        min_remaining_height = float('inf')

        for bin_id in offline_priority:
            bin = all_bins[bin_id]
            position = (0, bin.get_current_height(), 0)
            if bin.can_place(item, position):
                adjusted_item_height = utils.get_adjusted_height(item.placed_dimensions[1], bin.min_adjust_length)
                remaining_height = bin_height - position[1] - adjusted_item_height
# 這邊好像怪怪的

                if (remaining_height < min_remaining_height) and (remaining_height >= 0):
                    min_remaining_height = remaining_height
                    best_position = position
                    item.placed_bin = bin.id
                    best_bin_id = bin_id
                    best_bin = bin
        
        # if best bin is found, put the item to the bin
        if best_bin_id is not None:
            best_bin = all_bins[best_bin_id]
            position = (0, best_bin.get_current_height(), 0)
            best_bin.place_item(item, best_position)
        # else: open a new bin
        else:
            unplaced_items.append(item)

    return unplaced_items