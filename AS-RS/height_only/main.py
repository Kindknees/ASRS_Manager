import pandas as pd
from item import Item
from ASRSManager import ASRSManager
import copy
from visualization.animation import create_animation
import yaml

if __name__ == '__main__':
    # ===============================================================
    # Initialization
    # ===============================================================
    # You can either provide a config file or specify the parameters directly.
    # If you provide a config file, it should be in YAML format with the required structure.
    # If you do not provide a config file, you must specify online_priority, offline_priority,
    # bin_dimensions, and weight_limit directly.
    # Here we use provide parameters directly for demonstration.
    
    # config = yaml.safe_load(open('./config.yaml', 'r'))
    # online_priority = config['online_priority']
    # offline_priority = config['offline_priority']
    # bin_width = config['bin_config']['width']
    # bin_height = config['bin_config']['height']
    # bin_depth = config['bin_config']['depth']
    # bin_min_adjust_length = config['bin_config']['min_adjust_length']
    # bin_dimensions = (bin_width, bin_height, bin_depth, bin_min_adjust_length)
    # weight_limit = config.get('weight_limit', None)

    # manager = ASRSManager(online_priority=online_priority,
    #                        offline_priority=offline_priority,
    #                        bin_dimensions=bin_dimensions,
    #                        weight_limit=weight_limit)

    # Or, you can just set up the manager with a config file path:
    manager = ASRSManager(
        config_path='./config.yaml'
    )

    # ===============================================================
    # Function 1: Online Operation
    # ===============================================================
    # Here, we read items from a CSV file and place them online to simulate the ASRS system.
    item_list = []
    df = pd.read_csv("./items.csv")
    for row in df.itertuples(index=False):
        item_list.append(Item(row.width, row.height, row.depth, row.can_rotate, row.weight, row.id, False))

    online_history = [copy.deepcopy(manager.bins)]  # to create an animation later
    placed_sequence = [None]
    plan_history = [] 
    # start to place items online
    for item in item_list:
        result = manager.place_item_online(item)
        if result is not None:
            online_history.append(copy.deepcopy(manager.bins))
            placed_sequence.append(copy.deepcopy(item))
            plan_history.append(result)
            print ("Successfully placed item:", item.id)
        else:
            print(f"failed to place item {item.id} online.")

    create_animation(
        history=online_history,
        placed_item_sequence=placed_sequence,
        manager=manager,
        plan_history=plan_history,
        output_filename="online.gif"
    )

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
    retrieved_item_id = 1
    retrieved_item = manager.retrieve_item(retrieved_item_id)  # return an Item object or None if not found
    if retrieved_item:
        print(f"Retrieved item {retrieved_item.id} placed at bin {retrieved_item.placed_bin} at position {retrieved_item.position}.")
    else: 
        print(f"Item {retrieved_item_id} not found.")

    # ===============================================================
    # Function 4: Visualize Bins
    # ===============================================================
    bin_id_to_visualize = 2
    # manager.visualize_bins(bin_id=bin_id_to_visualize)
    
    # You can also save the visualization to a file by passing a save_path argument
    # manager.visualize_bins(bin_id=bin_id_to_visualize, save_path="./bin_visualization.png")

    # ===============================================================
    # Function 5: Remove Item
    # ===============================================================
    item_to_remove_id = 10

    # check the bin first
    retrieved_item = manager.retrieve_item(item_to_remove_id)
    placed_bin = retrieved_item.placed_bin
    print ("=== before removing ===")
    for i in manager.bins[placed_bin].items.values():
        print (f"Item {i.id} placed in bin {placed_bin} at position {i.position}")
    # manager.visualize_bins(bin_id=placed_bin)

    # then try to remove it and check
    status = manager.remove_item(item_to_remove_id)
    print ("=== after removing ===")
    for i in manager.bins[placed_bin].items.values():
        print (f"Item {i.id} placed in bin {placed_bin} at position {i.position}")
    # manager.visualize_bins(bin_id=placed_bin)

    # ===============================================================
    # Function 6: Create Animation
    # ===============================================================   
    # Create an animation for the online placement process
    # create_animation(
    #     history=online_history,
    #     placed_item_sequence=placed_sequence,
    #     manager=manager,
    #     plan_history=plan_history,
    #     output_filename="online.gif"
    # )