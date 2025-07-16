import itertools
from bin import Bin
from item import Item
from first_fit import FIRST_FIT
from best_fit import BEST_FIT
import pandas as pd

if __name__ == '__main__':
    # item list data
    # width, height, depth, rotation, id
    item_list_data = []
    df = pd.read_csv("./items.csv")
    for row in df.itertuples(index=False):
        width  = row.width
        height = row.height
        depth = row.depth
        rotation = row.can_rotate
        id = row.id
        item_list_data.append(Item(width, height, depth, rotation, id))

    # bin dimensions
    # width, height, depth, min_adjust_length
    bin_dimensions = (60, 200, 60, 5)

    # =================================================================
    # phase 1：Best Fit (Offline)
    # =================================================================
    print("--- Running Best Fit (Offline) Algorithm ---")
    bf_items_list = item_list_data.copy()
    bf_bins, bf_unplaced = BEST_FIT.best_fit(items=bf_items_list, bin_dimensions=bin_dimensions)
    
    print(f"Total bins used: {len(bf_bins)}")
    for i, bin_obj in enumerate(bf_bins):
        print(f"\nBin {i+1}:")
        print(f"  Number of items: {len(bin_obj.items)}")
        for item in bin_obj.items:
            print(f"  - Item {item.id} at {item.position} with dimensions {item.placed_dimensions}")

    if bf_unplaced:
        print("\nUnplaced items (too large for an empty bin):")
        for item in bf_unplaced:
            print(f"  - Item {item.id}")


    # =================================================================
    # phase 2：First Fit (Online)
    # =================================================================
    print("\n\n" + "="*50)
    print("--- Running First Fit (Online) Algorithm ---")
    
    ff_bins = []
    ff_unplaced = []
    ff_item_list = item_list_data.copy()
    
    for item in ff_item_list:
        was_placed = FIRST_FIT.first_fit(ff_bins, item, bin_dimensions)
        if was_placed is False:
            ff_unplaced.append(item)

    print("\n--- Final State for First Fit ---")
    print(f"Total bins used: {len(ff_bins)}")
    for i, bin_obj in enumerate(ff_bins):
        print(f"\nBin {i+1}:")
        print(f"  Number of items: {len(bin_obj.items)}")
        for item in bin_obj.items:
            print(f"  - Item {item.id} at {item.position} with dimensions {item.placed_dimensions}")

    if ff_unplaced:
        print("\nUnplaced items (too large for an empty bin):")
        for item in ff_unplaced:
            print(f"  - Item {item.id}")
