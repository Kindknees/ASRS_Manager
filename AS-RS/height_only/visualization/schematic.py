import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MaxNLocator

def plot_cuboid_with_cuts(x_range, y_range, z_range, num_yz_cuts=3, num_xz_cuts=2):
    """
    繪製一個長方體，並在 YZ 平面（x 值固定）和 XZ 平面（y 值固定）上繪製切割線，
    移除 YZ 平面上的網狀格線。

    參數:
    x_range (tuple): 長方體在 X 軸上的範圍 (x_min, x_max)。
    y_range (tuple): 長方體在 Y 軸上的範圍 (y_min, y_max)。
    z_range (tuple): 長方體在 Z 軸上的範圍 (z_min, z_max)。
    num_yz_cuts (int): 要在 X 軸上切割的 YZ 平面數量。
    num_xz_cuts (int): 要在 Y 軸上切割的 XZ 平面數量。
    """
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    x_min, x_max = x_range
    y_min, y_max = y_range
    z_min, z_max = z_range

    # 定義長方體的八個頂點
    vertices = np.array([
        (x_min, y_min, z_min), (x_max, y_min, z_min),
        (x_max, y_max, z_min), (x_min, y_max, z_min),
        (x_min, y_min, z_max), (x_max, y_min, z_max),
        (x_max, y_max, z_max), (x_min, y_max, z_max)
    ])

    # 定義長方體的邊
    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0),  # 底面
        (4, 5), (5, 6), (6, 7), (7, 4),  # 頂面
        (0, 4), (1, 5), (2, 6), (3, 7)   # 垂直邊
    ]

    # 繪製長方體的邊
    for i, j in edges:
        ax.plot3D(*zip(vertices.take(i, axis=0), vertices.take(j, axis=0)), color='b')

    # 繪製 YZ 平面切割線
    if num_yz_cuts > 0:
        cut_x_values = np.linspace(x_min, x_max, num_yz_cuts + 2)[1:-1]
        for x_cut in cut_x_values:
            ax.plot([x_cut, x_cut], [y_min, y_max], [z_min, z_min], color='r', linestyle='--')
            ax.plot([x_cut, x_cut], [y_min, y_max], [z_max, z_max], color='r', linestyle='--')
            ax.plot([x_cut, x_cut], [y_min, y_min], [z_min, z_max], color='r', linestyle='--')
            ax.plot([x_cut, x_cut], [y_max, y_max], [z_min, z_max], color='r', linestyle='--')

    # 繪製 XZ 平面切割線
    # if num_xz_cuts > 0:
    #     cut_y_values = np.linspace(y_min, y_max, num_xz_cuts + 2)[1:-1]
    #     for y_cut in cut_y_values:
    #         ax.plot([x_min, x_max], [y_cut, y_cut], [z_min, z_min], color='g', linestyle='--')
    #         ax.plot([x_min, x_max], [y_cut, y_cut], [z_max, z_max], color='g', linestyle='--')
    #         ax.plot([x_min, x_min], [y_cut, y_cut], [z_min, z_max], color='g', linestyle='--')
    #         ax.plot([x_max, x_max], [y_cut, y_cut], [z_min, z_max], color='g', linestyle='--')

    # 設定軸標籤
    ax.set_xlabel('X', loc="right")
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    # 設定軸的範圍
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.set_zlim(z_min, z_max)

    x_len = x_max - x_min
    y_len = y_max - y_min
    z_len = z_max - z_min

    # 設定 box_aspect 讓軸的視覺長度與數據長度成比例
    # 這裡我們讓最長軸的比例為 1，其他軸按比例縮放
    max_len = max(x_len, y_len, z_len)
    ax.set_box_aspect([x_len / max_len, y_len / max_len, z_len / max_len])
    # ax.set_box_aspect([x_len / min_len, y_len / min_len, z_len / min_len])
    ax.yaxis.set_major_locator(MaxNLocator(nbins=4))
    ax.zaxis.set_major_locator(MaxNLocator(nbins=5))

    plt.show()

# 範例使用：
# 定義長方體的範圍
x_min, x_max = 0, 450
y_min, y_max = 0, 50
z_min, z_max = 0, 200

# 繪製長方體並切割成 2 個 YZ 平面和 2 個 XZ 平面
plot_cuboid_with_cuts((x_min, x_max), (y_min, y_max), (z_min, z_max), num_yz_cuts=8, num_xz_cuts=0)

# 如果你不想顯示任何切割線，可以設定 num_yz_cuts=0 和 num_xz_cuts=0
# plot_cuboid_with_cuts((x_min, x_max), (y_min, y_max), (z_min, z_max), num_yz_cuts=0, num_xz_cuts=0)