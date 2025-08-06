from bin import Bin
import utils
from item import Item

def first_fit(item_to_place:Item, all_bins, online_priority:list, bin_dimensions:tuple, best_pallet: Item):
    """
    Implements the First Fit algorithm for placing an item into bins.

    :param item_to_place: Item object to be placed.
    :param all_bins: A dictionary of Bin objects {id: Bin}.
    :param online_priority: A list of bin IDs representing the order in which to try placing the item.
    :param bin_dimensions: A tuple representing the dimensions of the bins (width, height, depth, min_adjust_length).
    :return: The ID of the bin where the item
    """

    item_dimension = utils.get_optimal_dimension(item_to_place, bin_dimensions)
    
    if item_dimension is None:
        raise ValueError (f"Item {item_to_place.id} cannot be placed due to dimension constraints.")
        # item_to_place.placed_bin = None
        # item_to_place.position = None
        # item_to_place.placed_dimensions = None
        # return None

    best_bin = None
    for bin_id in online_priority:
        bin = all_bins[bin_id]
        if bin.weight_limit != None:
            if bin.weight_limit < item_to_place.weight:
                continue
        if bin.can_place(item_to_place):
            best_bin = bin
            break
    if best_bin is None:
        raise ValueError(f"Item {item_to_place.id} cannot be placed in any bin due to running out of space.")

    return {
        'pallet_id': best_pallet.id if best_pallet else None,
        'original_pallet_placed_bin': best_pallet.placed_bin if best_pallet else None,
        'original_pallet_position': best_pallet.position if best_pallet else None,
        'target_bin': best_bin.id if best_bin else None,
        'target_position': (0, best_bin.get_current_height(), 0) if best_bin else None,
    }
        
            
    # item_to_place.placed_bin = None
    # item_to_place.position = None
    # item_to_place.placed_dimensions = None
    # print (f"Cannot place item {item_to_place.id} into bins due to weight constraints or the bins are full.")
    # return None