import itertools
from bin import Bin
from item import Item
import utils

class BEST_FIT:
    """
    Implements the Best Fit (Offline) algorithm for 1D bin packing.

    This algorithm is tailored for vertical stacking scenarios, where the primary
    goal is to minimize the total height of items in each bin. It processes
    the entire list of items at once to find an optimized placement.
    """

    @staticmethod
    def best_fit(items:list, bin_dimensions):
        """
        Applies the offline Best Fit algorithm to pack 3D items into bins.

        This method first sorts items by height. For each item, if it is rotatable, it determines
        an optimal, height-minimized orientation. It then searches all existing
        bins to find the placement that results in the lowest new total height.
        If no suitable space is found in existing bins, a new bin is created.

        :param items: A list of Item objects to be packed.
        :param bin_dimensions: A tuple representing the dimensions
                               (width, height, depth, min_adjust_length) of the bins.
        :return: A tuple containing two lists: (list of used Bin objects,
                 list of unplaced Item objects).
        """
        bins = []
        unplaced_items = []
        bin_width, bin_height, bin_depth, bin_min_adjust_length = bin_dimensions

        # rotate items to height-minimized orientation
        for item in items:
            optimal_orientation = utils.get_optimal_dimension(item, bin_dimensions)
            
            if optimal_orientation is None:
                unplaced_items.append(item)
                continue  
            item.placed_dimensions = optimal_orientation
        # print (f"original items: {[i.id for i in items[:10]]}")
        items.sort(key=lambda i: i.placed_dimensions[1], reverse=True)
        # print (f"sorted items: {[i.id for i in items[:10]]}")

        #best fit algorithm start
        for item in items:
            best_bin = None
            best_position = None
            # scoring: # find the bin that results in the lowest new total height
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
                if new_bin.can_place(item, (0, 0, 0)):
                    new_bin.place_item(item, (0, 0, 0))
                    bins.append(new_bin)
                else:
                    unplaced_items.append(item)

        return bins, unplaced_items