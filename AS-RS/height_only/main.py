import pandas as pd
from item import Item
from ASRSManager import ASRSManager

if __name__ == '__main__':

    manager = ASRSManager(config_path='./config.yaml')

    # ===============================================================
    # Phase 1: Online Operation
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
    # Phase 2: Offline Reorganization
    # ===============================================================
    
    reorg_result = manager.reorganize_offline()

    if reorg_result:
        print(f"reorganization successful!")
    else:
        print(f"reorganization failed.")