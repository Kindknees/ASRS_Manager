import matplotlib.pyplot as plt
import numpy as np

def plot_bin(bins, bin_id, save_path=None):
    """
    視覺化指定儲位(bin)中的物品分佈，並在每個物品上顯示其 ID。
    """
    bin = bins[bin_id]

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    # 繪製儲位的紅色虛線外框
    xx, yy = np.meshgrid(np.linspace(0, bin.width, 2), np.linspace(0, bin.depth, 2))
    zz_top = np.full_like(xx, bin.height)
    ax.plot_wireframe(xx, yy, zz_top, color="red", linestyle='--')

    colors = plt.cm.rainbow(np.linspace(0, 1, len(bin.items)))

    for item, color in zip(bin.items, colors):
        x, y, z = item.position
        dx, dy, dz = item.placed_dimensions

        ax.bar3d(x, z, y, dx, dz, dy, color=color, alpha=0.8, edgecolor='k')

        # 在物品中心顯示 ID 
        # 計算文字要放置的座標
        text_x = x + dx / 2
        text_y = z + dz / 2     # Y 軸在圖上對應的是 depth
        text_z = y + dy / 2     # Z 軸在圖上對應的是 height

        # 加上文字
        ax.text(text_x, text_y, text_z, f"ID:{item.id}",
        ha='center',
        va='center',
        color='black',
        fontweight='bold',
        bbox=dict(facecolor='white',  # 背景框顏色
                  alpha=1,         # 背景透明度 (0=全透明, 1=不透明)
                  edgecolor='none',  # 無邊框
                  boxstyle='round,pad=0.2'))

    ax.set_xlabel('Width (X)')
    ax.set_ylabel('Depth (Y)')
    ax.set_zlabel('Height (Z)')
    ax.set_title(f'Bin {bin.id} (with {len(bin.items)} items)')

    ax.set_xlim([0, bin.width])
    ax.set_ylim([0, bin.depth])
    ax.set_zlim([0, bin.height])

    ax.view_init(azim=-120)

    if save_path:
        plt.savefig(save_path)
        print(f"Bin visualization saved to {save_path}")
    else:
        plt.show()