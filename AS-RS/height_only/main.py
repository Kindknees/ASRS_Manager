import itertools
from bin import Bin
from item import Item
from first_fit import FIRST_FIT
from best_fit import BEST_FIT
import pandas as pd

if __name__ == '__main__':
    # --- 貨物清單定義 ---
    # width, height, depth, rotation, id=None
    item_list_data = []
    df = pd.read_csv("./items.csv")
    for row in df.itertuples(index=False):
        width  = row.width
        height = row.height
        depth = row.depth
        rotation = row.can_rotate
        id = row.id
        item_list_data.append(Item(width, height, depth, rotation, id))

    # --- 一個櫃子的尺寸 ---
    # 寬度、高度、深度、最小調整長度
    bin_dimensions = (60, 200, 60, 5)

    # =================================================================
    # 情境一：Best Fit (Offline) - 拿到完整清單一次性處理
    # =================================================================
    print("--- Running Best Fit (Offline) Algorithm ---")
    # 每次都要重新創建物品列表，因為演算法會修改物品的內部狀態
    
    bf_bins, bf_unplaced = BEST_FIT.best_fit(items=item_list_data, bin_dimensions=bin_dimensions)
    
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
    # 情境二：First Fit (Online) - 模擬物品一件件到達
    # =================================================================
    print("\n\n" + "="*50)
    print("--- Running First Fit (Online) Algorithm ---")
    
    ff_bins = []
    ff_unplaced = []
    
    # 模擬物品一件件地進入系統
    for item in item_list_data:
        was_placed = FIRST_FIT.first_fit_1D_stacking(ff_bins, item, bin_dimensions)
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
