import pandas as pd
from item import Item
from ASRSManager import ASRSManager

if __name__ == '__main__':

    manager = ASRSManager(config_path='./config.yaml')

    # ===============================================================
    # Function 1: Online Operation
    # ===============================================================
    item_list = []
    df = pd.read_csv("./items.csv")
    for row in df.itertuples(index=False):
        item_list.append(Item(row.width, row.height, row.depth, row.can_rotate, row.weight, row.id))

    # start to place items online
    for item in item_list:
        result = manager.place_item_online(item)
        
        if not result:
            print(f"failed to place item {item.id} online.")

    # ===============================================================
    # Function 2: Offline Reorganization
    # ===============================================================
    
    reorg_result = manager.reorganize_offline()

    if reorg_result:
        print(f"reorganization successful!")
    else:
        print(f"reorganization failed.")

    # ===============================================================
    # Function 3: Retrieve Items
    # ===============================================================
    retrieved_item_id = 10
    retrieved_item = manager.retrieve_item(retrieved_item_id)  # return an item object or None if not found
    if retrieved_item:
        print(f"Retrieved item {retrieved_item.id} placed at bin {retrieved_item.placed_bin} at position {retrieved_item.position}.")
    else: 
        print(f"Item {retrieved_item_id} not found.")

    # ===============================================================
    # Function 4: Visualize Bins
    # ===============================================================
    bin_id_to_visualize = 2
    manager.visualize_bins(bin_id=bin_id_to_visualize)
    # You can also save the visualization to a file by passing a save_path argument
    # manager.visualize_bins(bin_id=bin_id_to_visualize, save_path="./bin_visualization.png")