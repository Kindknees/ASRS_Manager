import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import pandas as pd
import random
import copy
from mpl_toolkits.mplot3d.art3d import Poly3DCollection 

from item import Item
from ASRSManager import ASRSManager

def plot_cuboid(ax, position, dimensions, color='b', alpha=0.1):
    """
    plot items in bins

    :param ax: Matplotlib 3D onject.
    :param position: (x, y, z) origin of the cuboid.
    :param dimensions: (width, height, depth) size of cuboid.
    :param color: default'b'
    :param alpha: opacity.
    """
    x, z, y = position
    w, h, d = dimensions

    vertices = [
        (x, y, z), (x + w, y, z), (x + w, y + d, z), (x, y + d, z),
        (x, y, z + h), (x + w, y, z + h), (x + w, y + d, z + h), (x, y + d, z + h)
    ]

    faces = [
        [vertices[0], vertices[1], vertices[2], vertices[3]],
        [vertices[4], vertices[5], vertices[6], vertices[7]],
        [vertices[0], vertices[1], vertices[5], vertices[4]],
        [vertices[2], vertices[3], vertices[7], vertices[6]],
        [vertices[1], vertices[2], vertices[6], vertices[5]],
        [vertices[4], vertices[7], vertices[3], vertices[0]]
    ]

    poly3d = Poly3DCollection(faces, facecolors=color, linewidths=0.5, edgecolors='k', alpha=alpha)
    ax.add_collection3d(poly3d)


def update_all_bins(frame, history, placed_item_sequence, bin_dimensions, fig, axs, item_colors, bin_ids):
    """
    Update all bins for the current animation frame.
    """
    # clear the axes for the current frame
    for ax in axs.flat:
        ax.cla()

    current_bins_state = history[frame]
    current_item = placed_item_sequence[frame]

    if current_item:
        title = f"Step {frame}: Placed Item ID {current_item.id} into Bin {current_item.placed_bin}"
    else:
        title = "Step 0: Initial State"
    fig.suptitle(title, fontsize=16)

    bin_w, bin_h, bin_d, _ = bin_dimensions

    for i, ax in enumerate(axs.flat):
        if i < len(bin_ids):
            bin_id = bin_ids[i]
            bin_obj = current_bins_state[bin_id]

            # draw the bin
            plot_cuboid(ax, (0, 0, 0), (bin_w, bin_h, bin_d), color='gray', alpha=0.05)

            # draw the items in the bin
            for item in bin_obj.items:
                plot_cuboid(ax, item.position, item.placed_dimensions, color=item_colors[item.id], alpha=0.7)

            ax.set_xlim(0, bin_w)
            ax.set_ylim(0, bin_d)
            ax.set_zlim(0, bin_h)
            ax.set_title(f"Bin {bin_id}")

            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_zticks([])

            # ax.set_xlabel('Width')
            # ax.set_ylabel('Depth')
            # ax.set_zlabel('Height')
            ax.set_title(f"Bin {bin_id}")
        else:
            ax.axis('off')


def create_animation(history, placed_item_sequence, manager, output_filename="asrs_full_system.gif"):
    """
    Create an animation of the ASRS system showing the online placement of items in bins.

    :param history: List of ASRSManager.bins at each step.
    :param placed_item_sequence: List of items placed at each step.
    :param manager: ASRSManager instance containing bin dimensions and other configurations.
    :param output_filename: Name of the output GIF file.
    """
    num_bins = len(manager.bins)
    nrows = 1
    ncols = num_bins

    fig, axs = plt.subplots(nrows, ncols, subplot_kw={"projection": "3d"}, figsize=(15, 12))

    all_item_ids = {item.id for item in placed_item_sequence if item is not None}
    item_colors = {item_id: (random.random(), random.random(), random.random()) for item_id in all_item_ids}

    bin_ids = sorted(manager.bins.keys())

    ani = FuncAnimation(fig, update_all_bins, frames=len(history),
                        fargs=(history, placed_item_sequence, manager.bin_dimensions, fig, axs, item_colors, bin_ids),
                        interval=500)   

    print("generating animation...")
    ani.save(output_filename, writer='pillow', dpi=100)
    print(f"gif saved as: {output_filename}")
    plt.close(fig)


if __name__ == '__main__':
    sim_manager = ASRSManager(config_path='./config.yaml')
    items_df = pd.read_csv("./items.csv")
    sim_item_list = [Item(row.width, row.height, row.depth, row.can_rotate, row.weight, row.id) for row in items_df.itertuples(index=False)]
    
    sim_history = [copy.deepcopy(sim_manager.bins)]
    sim_placed_sequence = [None]

    for item in sim_item_list:
        if sim_manager.place_item_online(item):
            sim_history.append(copy.deepcopy(sim_manager.bins))
            sim_placed_sequence.append(copy.deepcopy(item))

    create_animation(
        history=sim_history,
        placed_item_sequence=sim_placed_sequence,
        manager=sim_manager,
        output_filename="online.gif"
    )