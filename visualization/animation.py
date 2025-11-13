import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import random
from matplotlib.ticker import MaxNLocator
from item import Item
from ASRSManager import ASRSManager

def plot_cuboid(ax, position, dimensions, color='blue', alpha=0.8, x_offset=0):
    """
    Plots a cuboid on the given 3D axes with an x_offset.
    """
    # item position: (x, y, z) -> (width, height, depth)
    # The plot's axes: (x, y, z) -> (width, depth, height)
    x, z, y = position
    w, h, d = dimensions
    ax.bar3d(x + x_offset, z, y, w, d, h, color=color, alpha=alpha, edgecolor='k')

def update_all_bins(frame, history, placed_item_sequence, plan_history, manager, fig, ax, item_colors, pallet_to_item_map, empty_pallet_color):
    """
    Updates the state of all bins for each frame in the animation on a single axis.
    """
    ax.cla()

    bin_w, bin_h, bin_d, _ = manager.bin_dimensions
    gap = bin_w * 0.1 # 10% of bin width as gap

    # --- Set Title ---
    if frame == 0:
        title = "Step 0: Initial State with Empty Pallets"
    else:
        plan = plan_history[frame - 1]
        item = placed_item_sequence[frame]
        title = f"Step {frame}: Use Pallet {plan['pallet_id']} for Item {item.pallet_id}, Placed in Bin {plan['target_bin']}"
    fig.suptitle(title, fontsize=16)

    current_bins_state = history[frame]
    
    if frame > 0:
        plan = plan_history[frame - 1]
        pallet_id = plan['pallet_id']
        if pallet_id not in pallet_to_item_map:
            if item_colors:
                pallet_to_item_map[pallet_id] = item_colors.pop(0)
            else:
                pallet_to_item_map[pallet_id] = (random.random(), random.random(), random.random())

    # --- Draw each bin ---
    bin_ids = sorted(current_bins_state.keys(), key=int)
    total_width = 0
    for i, bin_id in enumerate(bin_ids):
        bin_obj = current_bins_state[bin_id]
        x_offset = i * (bin_w + gap)
        
        # Define the vertices of the bin cuboid
        vertices = np.array([
            (x_offset, 0, 0), (x_offset + bin_w, 0, 0),
            (x_offset + bin_w, bin_d, 0), (x_offset, bin_d, 0),
            (x_offset, 0, bin_h), (x_offset + bin_w, 0, bin_h),
            (x_offset + bin_w, bin_d, bin_h), (x_offset, bin_d, bin_h)
        ])

        # Define the edges of the bin cuboid
        edges = [
            (0, 1), (1, 2), (2, 3), (3, 0),
            (4, 5), (5, 6), (6, 7), (7, 4),
            (0, 4), (1, 5), (2, 6), (3, 7)
        ]

        # Draw the bin wireframe
        for start, end in edges:
            ax.plot3D(*zip(vertices[start], vertices[end]), color="red", linestyle='--')
        
        # Add bin ID text
        ax.text(x_offset + bin_w / 2, -gap*2 , bin_h + gap*2, f'Bin {bin_id}', ha='center')


        # Draw items in the bin
        for item_id, item in bin_obj.items.items():
            color_to_use = empty_pallet_color
            if not item.empty:
                color_to_use = pallet_to_item_map.get(item.pallet_id, 'magenta')
            
            # Map item.position y to plot z, and item.position z to plot y
            plot_pos = (item.position[0], item.position[2], item.position[1])
            plot_cuboid(ax, plot_pos, item.placed_dimensions, color=color_to_use, x_offset=x_offset)
        
        total_width = x_offset + bin_w

    # --- Set overall axes properties ---
    ax.set_xlabel('Width (X)')
    ax.set_ylabel('Depth (Y)')
    ax.set_zlabel('Height (Z)')

    ax.grid(False)

    ax.set_xlim([0, total_width])
    ax.set_ylim([0, bin_d])
    ax.set_zlim([0, bin_h])

    ax.set_box_aspect((total_width, bin_d, bin_h)) 

    ax.view_init(azim=90, elev=0)

    ax.yaxis.set_major_locator(MaxNLocator(nbins=3))
    ax.zaxis.set_major_locator(MaxNLocator(nbins=4))


def create_animation(history: list, placed_item_sequence: list, manager: ASRSManager, plan_history: list, output_filename: str = "online.gif"):
    """
    Creates and saves a GIF animation of the ASRS system.
    """
    fig = plt.figure(figsize=(20, 8))
    ax = fig.add_subplot(111, projection='3d')
    fig.subplots_adjust(
        left=0.05,
        right=0.95,
        bottom=0.05,
        top=0.9,
        wspace=0.1,
        hspace=0.1 
    )

    # --- Prepare colors ---
    item_ids = [item.pallet_id for item in placed_item_sequence if item is not None]
    colormap = plt.get_cmap('tab20', len(item_ids) if len(item_ids) > 0 else 1)
    item_colors_list = [colormap(i) for i in range(len(item_ids))]
    random.shuffle(item_colors_list)
    
    pallet_to_item_map = {}
    empty_pallet_color = 'lightblue'

    # --- Create Animation ---
    print("Generating animation... This may take a few moments.")
    ani = FuncAnimation(fig, update_all_bins, frames=len(history),
                        fargs=(history, placed_item_sequence, plan_history, manager, fig, ax, item_colors_list, pallet_to_item_map, empty_pallet_color),
                        interval=1500, repeat=False)

    # --- Save GIF ---
    try:
        ani.save(output_filename, writer='pillow', dpi=100)
        print(f"Successfully saved animation to '{output_filename}'")
    except Exception as e:
        print(f"Error saving animation: {e}")
        print("Please make sure you have 'Pillow' installed (`pip install Pillow`).")
    
    plt.close(fig)