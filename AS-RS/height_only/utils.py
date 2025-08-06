import math
import itertools
from item import Item

def get_adjusted_height(item_height_value, min_adjust_length):
    if min_adjust_length <= 0:
        return item_height_value
    return math.ceil(item_height_value / min_adjust_length) * min_adjust_length

def get_optimal_dimension(item: Item, bin_dimensions):
        """
        return: best (width, height, depth) tuple. If the item does not fit the bin, return None。
        """
        dims = [item.width, item.height, item.depth]
        bin_width, bin_height, bin_depth = bin_dimensions[:3]
        
        if item.rotation == 0:
            # not rotatable
            if (dims[0] <= bin_width and dims[2] <= bin_depth):
                return tuple(dims)
            
            elif(dims[2] <= bin_width and dims[0] <= bin_depth):
                new_dims = [dims[2], dims[1], dims[0]]
                return tuple(new_dims)
            else:
                return None

        # generate all dimensions (width, height, depth)
        possible_orientations = list(set(itertools.permutations(dims)))
        
        valid_orientations = []
        for w, h, d in possible_orientations:
            if (w <= bin_width and h <= bin_height and d <= bin_depth):
               valid_orientations.append((w, h, d))
            elif(d <= bin_width and h <= bin_height and w <= bin_depth):
                valid_orientations.append((d, h, w))
        
        if not valid_orientations:
            return None
            
        valid_orientations.sort(key=lambda o: o[1])
        return valid_orientations[0]

def ItemDictToItem(item_dict):
    """
    Convert a dictionary representation of an item to an Item object.
    """
    item = Item(
        width=item_dict['width'],
        height=item_dict['height'],
        depth=item_dict['depth'],
        rotation=item_dict['rotation'],
        weight=item_dict['weight'],
        id=item_dict['id'],
        empty=item_dict['empty'],
    )
    item.position = item_dict.get('position', None)
    item.placed_bin = item_dict.get('placed_bin', None)
    item.placed_dimensions = item_dict.get('placed_dimensions', (item.width, item.height, item.depth))
    return item