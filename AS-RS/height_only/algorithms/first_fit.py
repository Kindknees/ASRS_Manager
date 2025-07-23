from bin import Bin
import utils

def first_fit(item_to_place, all_bins, online_priority:list, bin_dimensions):
    """
    Implements the First Fit algorithm for placing an item into bins.
    
    :param item_to_place: Item object to be placed.
    :param all_bins: A dictionary of Bin objects {id: Bin}.
    :param online_priority: A list of bin IDs representing the order in which to try placing the item.
    :param bin_dimensions: A tuple representing the dimensions of the bins (width, height, depth, min_adjust_length).
    :return: The ID of the bin where the item
    """
    bin_width, bin_height, bin_depth, bin_min_adjust_length = bin_dimensions
    item_dimension = utils.get_optimal_dimension(item_to_place, bin_dimensions)
    
    if item_dimension is None:
        print (f"Item {item_to_place.id} cannot be placed due to dimension constraints.")
        item_to_place.placed_bin = None
        item_to_place.position = None
        item_to_place.placed_dimensions = None
        return None

    for bin_id in online_priority:
        bin = all_bins[bin_id]
        if bin.weight_limit != None:
            if bin.weight_limit < item_to_place.weight:
                continue
        
        current_stacked_height = bin.get_current_height()
        w, h, d = item_dimension
        item_to_place.placed_dimensions = (w, h, d)
        adjusted_height = utils.get_adjusted_height(h, bin.min_adjust_length)

        if current_stacked_height + adjusted_height <= bin.height:
            position = (0, current_stacked_height, 0)
            if w <= bin.width and d <= bin.depth:
                bin.place_item(item_to_place, position)
                return bin_id
            
    item_to_place.placed_bin = None
    item_to_place.position = None
    item_to_place.placed_dimensions = None
    print (f"Cannot place item {item_to_place.id} into bins due to weight constraints or the bins are full.")
    return None