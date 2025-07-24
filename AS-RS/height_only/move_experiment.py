import pandas as pd
from item import Item
from ASRSManager import ASRSManager

if __name__ == '__main__':

    manager = ASRSManager(config_path='./config.yaml')

    # ===============================================================
    # 1: Online Operation, with nearest bin first fit algorithm
    # ===============================================================
    print ("=====online with nearest bin first fit algorithm=====")
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
    vertical_distance = 0
    horizontal_distance = 0
    for item in item_list:
        retrieved_item = manager.retrieve_item(item.id)
        if retrieved_item:
            item_position_online[item.id] = (item.placed_bin, retrieved_item.position)
            # 假設貨物都從第5號bin的中間放入：
            # print (f"processing item {retrieved_item.id}")
            vertical_distance += manager.bin_dimensions[1] * abs(retrieved_item.placed_dimensions[1] - manager.bin_dimensions[1]/2)
            horizontal_distance += manager.bin_dimensions[0] * abs(retrieved_item.placed_bin - 5)
            
    total_length_online += vertical_distance + horizontal_distance
    for bin in manager.bins.values():
        print(f"Bin {bin.id} has items: {[item.id for item in bin.items]}")

    print (f"Total horizontal distance of items placed online: {horizontal_distance}")
    print (f"Total vertical distance of items placed online: {vertical_distance}")
    print(f"Total length of items placed online: {total_length_online}")


    # ===============================================================
    # 2: Offline Reorganization
    # ===============================================================
    print ("=====offline reorganization=====")
    reorg_result = manager.reorganize_offline()

    total_length_offline = 0
    vertical_distance = 0
    horizontal_distance = 0
    if reorg_result:
        print(f"reorganization successful!")
        for item in item_list:
            retrieved_item = manager.retrieve_item(item.id)
            if retrieved_item is not None:
                vertical_distance += abs(retrieved_item.placed_dimensions[1] - item_position_online[retrieved_item.id][1][1])
                horizontal_distance += manager.bin_dimensions[0] * abs(retrieved_item.placed_bin - item_position_online[retrieved_item.id][0])
        
        total_length_offline += vertical_distance + horizontal_distance
        print(f"Total horizontal distance of items moved offline: {horizontal_distance}")
        print(f"Total vertical distance of items moved offline: {vertical_distance}")
        print (f"Total length of moving items offline: {total_length_offline}")
    else:
        print(f"reorganization failed.")

    for bin in manager.bins.values():
        print(f"Bin {bin.id} has items: {[item.id for item in bin.items]}")


    ## ===============================================================
    # 3: Online Operation, without nearest bin first fit algorithm
    # ===============================================================
    print ("=====online without nearest bin first fit algorithm=====")
    import yaml
    with open('./config.yaml', 'r') as file:
        config = yaml.safe_load(file)
        bin_config = config['bin_config']
        bin_dimensions = (bin_config['width'], bin_config['height'], bin_config['depth'], bin_config['min_adjust_length'])
        weight_limit = bin_config.get('weight_limit', None)
    
    manager = ASRSManager(
        online_priority=[i for i in range(1, 10)],
        offline_priority=[i for i in range(1, 10)],
        bin_dimensions=bin_dimensions,
        weight_limit=weight_limit
    )
    for item in item_list:
        result = manager.place_item_online(item)
        
        if not result:
            print(f"failed to place item {item.id} online.")
    
    item_position_online = {}
    total_length_online = 0
    vertical_distance = 0
    horizontal_distance = 0
    for item in item_list:
        retrieved_item = manager.retrieve_item(item.id)
        if retrieved_item:
            item_position_online[item.id] = (item.placed_bin, retrieved_item.position)
            # 假設貨物都從第10號bin的中間放入：
            # print (f"processing item {retrieved_item.id}")
            vertical_distance += manager.bin_dimensions[1] * abs(retrieved_item.placed_dimensions[1] - manager.bin_dimensions[1]/2)
            horizontal_distance += manager.bin_dimensions[0] * abs(retrieved_item.placed_bin - 5)
            
    total_length_online += vertical_distance + horizontal_distance
    for bin in manager.bins.values():
        print(f"Bin {bin.id} has items: {[item.id for item in bin.items]}")

    print (f"Total horizontal distance of items placed online: {horizontal_distance}")
    print (f"Total vertical distance of items placed online: {vertical_distance}")
    print(f"Total length of items placed online: {total_length_online}")

    # ===============================================================
    # 4: Offline Reorganization, without nearest bin first fit algorithm
    # ===============================================================
    print ("=====offline reorganization without nearest bin first fit algorithm=====")
    reorg_result = manager.reorganize_offline()
    reorg_result = manager.reorganize_offline()

    total_length_offline = 0
    vertical_distance = 0
    horizontal_distance = 0
    if reorg_result:
        print(f"reorganization successful!")
        for item in item_list:
            retrieved_item = manager.retrieve_item(item.id)
            if retrieved_item is not None:
                vertical_distance += abs(retrieved_item.placed_dimensions[1] - item_position_online[retrieved_item.id][1][1])
                horizontal_distance += manager.bin_dimensions[0] * abs(retrieved_item.placed_bin - item_position_online[retrieved_item.id][0])
        
        total_length_offline += vertical_distance + horizontal_distance
        print(f"Total horizontal distance of items moved offline: {horizontal_distance}")
        print(f"Total vertical distance of items moved offline: {vertical_distance}")
        print (f"Total length of moving items offline: {total_length_offline}")
    else:
        print(f"reorganization failed.")