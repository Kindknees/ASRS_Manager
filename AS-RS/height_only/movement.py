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
    
    item_position_online = {}
    total_length_online = 0
    for item in item_list:
        retrieved_item = manager.retrieve_item(item.id)
        if retrieved_item:
            item_position_online[item.id] = (item.placed_bin, retrieved_item.position)
            # 假設貨物都從第10號bin的中間放入：
            # print (f"processing item {retrieved_item.id}")
            total_length_online += abs(retrieved_item.placed_dimensions[1] - manager.bin_dimensions[1]/2) + manager.bin_dimensions[0] * abs(retrieved_item.placed_bin - 10)
    
    for bin in manager.bins.values():
        print(f"Bin {bin.id} has items: {[item.id for item in bin.items]}")
    
    print(f"Total length of items placed online: {total_length_online}")


    # ===============================================================
    # Function 2: Offline Reorganization
    # ===============================================================
    
    reorg_result = manager.reorganize_offline()

    total_length_offline = 0
    if reorg_result:
        print(f"reorganization successful!")
        for item in item_list:
            retrieved_item = manager.retrieve_item(item.id)
            if retrieved_item is not None:
                total_length_offline += abs(retrieved_item.placed_dimensions[1] - item_position_online[retrieved_item.id][1][0]) + \
                    manager.bin_dimensions[0] * abs(retrieved_item.placed_bin - item_position_online[retrieved_item.id][0])
        print (f"Total length of moving items offline: {total_length_offline}")
    else:
        print(f"reorganization failed.")

    # ===============================================================
    for bin in manager.bins.values():
        print(f"Bin {bin.id} has items: {[item.id for item in bin.items]}")