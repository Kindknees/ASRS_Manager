import matplotlib.pyplot as plt
import numpy as np

def plot_bins(bins, bin_dimensions, title):
    bin_width, bin_height, bin_depth, _ = bin_dimensions

    for i, bin_obj in enumerate(bins):
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')

        xx, yy = np.meshgrid(np.linspace(0, bin_width, 2), np.linspace(0, bin_depth, 2))
        zz_top = np.full_like(xx, bin_height)

        ax.plot_wireframe(xx, yy, zz_top, color="red", linestyle='--')

        colors = plt.cm.rainbow(np.linspace(0, 1, len(bin_obj.items)))

        for item, color in zip(bin_obj.items, colors):
            x, y, z = item.position
            dx, dy, dz = item.placed_dimensions
            ax.bar3d(x, z, y, dx, dz, dy, color=color, alpha=0.8, edgecolor='k')

        ax.set_xlabel('width (x)')
        ax.set_ylabel('depth (y)')
        ax.set_zlabel('height (z)')
        ax.set_title(f'{title} - bin {i+1} (with {len(bin_obj.items)} items)')

        ax.set_xlim([0, bin_width])
        ax.set_ylim([0, bin_depth])
        ax.set_zlim([0, bin_height])

        ax.view_init(azim=-120)
        
        plt.show()