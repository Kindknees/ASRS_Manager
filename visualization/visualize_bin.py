import matplotlib.pyplot as plt
import numpy as np

def plot_bin(bins, bin_id, save_path=None):
    """
    Visualizes a specific bin with its items in 3D.
    """
    bin = bins[bin_id]

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    xx, yy = np.meshgrid(np.linspace(0, bin.width, 2), np.linspace(0, bin.depth, 2))
    zz_top = np.full_like(xx, bin.height)
    ax.plot_wireframe(xx, yy, zz_top, color="red", linestyle='--')

    colors = plt.cm.rainbow(np.linspace(0, 1, len(bin.items)))

    for item, color in zip(bin.items.values(), colors):
        x, y, z = item.position
        dx, dy, dz = item.placed_dimensions

        ax.bar3d(x, z, y, dx, dz, dy, color=color, alpha=0.8, edgecolor='k')

        text_x = x + dx / 2
        text_y = z + dz / 2     # depth
        text_z = y + dy / 2     # height

        ax.text(text_x, text_y, text_z, f"ID:{item.pallet_id}",
        ha='center',
        va='center',
        color='black',
        fontweight='bold',
        bbox=dict(facecolor='white',
                  alpha=1,
                  edgecolor='none',
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