import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import pandas as pd
import random
import copy
from mpl_toolkits.mplot3d.art3d import Poly3DCollection 

# 從您的專案中引入必要的類別
from item import Item
from ASRSManager import ASRSManager

def plot_cuboid(ax, position, dimensions, color='b', alpha=0.1):
    """
    在指定的 3D 軸上繪製一個長方體。
    :param ax: Matplotlib 3D 軸物件。
    :param position: (x, y, z) 方塊的起始點。
    :param dimensions: (width, height, depth) 方塊的尺寸。
    :param color: 顏色。
    :param alpha: 透明度。
    """
    x, z, y = position
    w, h, d = dimensions

    # 定義8個頂點
    vertices = [
        (x, y, z), (x + w, y, z), (x + w, y + d, z), (x, y + d, z),
        (x, y, z + h), (x + w, y, z + h), (x + w, y + d, z + h), (x, y + d, z + h)
    ]

    # 定義6個面，每個面由4個頂點組成
    faces = [
        [vertices[0], vertices[1], vertices[2], vertices[3]],
        [vertices[4], vertices[5], vertices[6], vertices[7]],
        [vertices[0], vertices[1], vertices[5], vertices[4]],
        [vertices[2], vertices[3], vertices[7], vertices[6]],
        [vertices[1], vertices[2], vertices[6], vertices[5]],
        [vertices[4], vertices[7], vertices[3], vertices[0]]
    ]

    # 使用 Poly3DCollection 創建 3D 物件
    poly3d = Poly3DCollection(faces, facecolors=color, linewidths=0.5, edgecolors='k', alpha=alpha)

    # 將 3D 物件加入到軸上
    ax.add_collection3d(poly3d)


# --- 動畫的核心更新函數 (新版本) ---
def update_all_bins(frame, history, placed_item_sequence, bin_dimensions, fig, axs, item_colors, bin_ids):
    """
    為所有貨櫃更新每一幀的畫面。
    """
    # 清除所有子圖
    for ax in axs.flat:
        ax.cla()

    current_bins_state = history[frame]
    current_item = placed_item_sequence[frame]

    # 設定主標題
    if current_item:
        title = f"Step {frame}: Placed Item ID {current_item.id} into Bin {current_item.placed_bin}"
    else:
        title = "Step 0: Initial State"
    fig.suptitle(title, fontsize=16)

    bin_w, bin_h, bin_d, _ = bin_dimensions

    # 遍歷每一個子圖和對應的貨櫃ID
    for i, ax in enumerate(axs.flat):
        if i < len(bin_ids):
            bin_id = bin_ids[i]
            bin_obj = current_bins_state[bin_id]

            # 繪製貨櫃外框
            plot_cuboid(ax, (0, 0, 0), (bin_w, bin_h, bin_d), color='gray', alpha=0.05)

            # 繪製貨櫃內的所有物品
            for item in bin_obj.items:
                plot_cuboid(ax, item.position, item.placed_dimensions, color=item_colors[item.id], alpha=0.7)

            # 設定子圖的座標軸和標題
            ax.set_xlim(0, bin_w)
            ax.set_ylim(0, bin_d)
            ax.set_zlim(0, bin_h)
            ax.set_title(f"Bin {bin_id}")
            # 簡化標籤，避免畫面擁擠
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_zticks([])

            ax.set_xlabel('Width')
            ax.set_ylabel('Depth')
            ax.set_zlabel('Height')
            ax.set_title(f"Bin {bin_id}")
        else:
            # 隱藏多餘的子圖
            ax.axis('off')


def create_full_system_animation(history, placed_item_sequence, manager, output_filename="asrs_full_system.gif"):
    """
    主函數：創建並儲存所有貨櫃的動畫。
    """
    num_bins = len(manager.bins)
    nrows = 1
    ncols = num_bins

    fig, axs = plt.subplots(nrows, ncols, subplot_kw={"projection": "3d"}, figsize=(15, 12))

    # 為每個物品ID生成一個隨機顏色
    all_item_ids = {item.id for item in placed_item_sequence if item is not None}
    item_colors = {item_id: (random.random(), random.random(), random.random()) for item_id in all_item_ids}

    # 獲取所有貨櫃的ID並排序，確保顯示順序固定
    bin_ids = sorted(manager.bins.keys())

    ani = FuncAnimation(fig, update_all_bins, frames=len(history),
                        fargs=(history, placed_item_sequence, manager.bin_dimensions, fig, axs, item_colors, bin_ids),
                        interval=500)

    print("generating animation...")
    ani.save(output_filename, writer='pillow', dpi=100) # 調整 dpi 來控制解析度
    print(f"gif saved as: {output_filename}")
    plt.close(fig) # 關閉圖形以釋放記憶體

# --- 整合與執行 ---
if __name__ == '__main__':
    # 1. 執行模擬並獲取歷史紀錄 (與之前相同)
    sim_manager = ASRSManager(config_path='./config.yaml')
    items_df = pd.read_csv("./items.csv")
    sim_item_list = [Item(row.width, row.height, row.depth, row.can_rotate, row.weight, row.id) for row in items_df.itertuples(index=False)]
    
    sim_history = [copy.deepcopy(sim_manager.bins)]
    sim_placed_sequence = [None]

    print("開始模擬線上放置過程...")
    for item in sim_item_list:
        if sim_manager.place_item_online(item):
            sim_history.append(copy.deepcopy(sim_manager.bins))
            sim_placed_sequence.append(copy.deepcopy(item))
    print("模擬完成。")

    # 2. 呼叫全系統動畫生成函數
    create_full_system_animation(
        history=sim_history,
        placed_item_sequence=sim_placed_sequence,
        manager=sim_manager,
        output_filename="asrs_full_system_online.gif"
    )