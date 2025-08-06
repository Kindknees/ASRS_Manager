import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import random
from matplotlib.ticker import MaxNLocator

# Use relative imports to correctly find modules in the parent directory
from item import Item
from ASRSManager import ASRSManager

def plot_cuboid(ax, position, dimensions, color='blue', alpha=0.8):
    """
    Plots a cuboid on the given 3D axes.
    """
    # item position: (x, y, z) -> (width, height, depth)
    # The plot's axes: (x, y, z) -> (width, depth, height)
    x, z, y = position
    w, h, d = dimensions
    ax.bar3d(x, z, y, w, d, h, color=color, alpha=alpha, edgecolor='k')

def update_all_bins(frame, history, placed_item_sequence, plan_history, manager, fig, axs, item_colors, pallet_to_item_map, empty_pallet_color):
    """
    Updates the state of all bins for each frame in the animation.
    """
    for ax in axs.flat:
        ax.cla()

    bin_w, bin_h, bin_d, _ = manager.bin_dimensions
    
    # --- Set Title ---
    if frame == 0:
        title = "Step 0: Initial State with Empty Pallets"
    else:
        plan = plan_history[frame - 1]
        item = placed_item_sequence[frame]
        title = f"Step {frame}: Use Pallet {plan['pallet_id']} for Item {item.id}, Placed in Bin {plan['target_bin']}"
    fig.suptitle(title, fontsize=16)

    current_bins_state = history[frame]
    
    # --- Assign a new color if a pallet is used for the first time ---
    if frame > 0:
        plan = plan_history[frame - 1]
        pallet_id = plan['pallet_id']
        if pallet_id not in pallet_to_item_map:
            if item_colors:
                pallet_to_item_map[pallet_id] = item_colors.pop(0)
            else:
                pallet_to_item_map[pallet_id] = (random.random(), random.random(), random.random())

    # --- Draw each bin ---
    bin_ids = sorted(current_bins_state.keys())
    for i, bin_id in enumerate(bin_ids):
        ax = axs.flat[i]
        bin_obj = current_bins_state[bin_id]
        
        # Draw bin wireframe
        xx, yy = np.meshgrid(np.linspace(0, bin_w, 2), np.linspace(0, bin_d, 2))
        zz_top = np.full_like(xx, bin_h)
        ax.plot_wireframe(xx, yy, zz_top, color="red", linestyle='--')

        # Set up axes properties
        ax.set_xlabel('Width')
        ax.set_ylabel('Depth')
        ax.set_zlabel('Height')
        ax.set_title(f'Bin {bin_id}')
        ax.set_xlim([0, bin_w])
        ax.set_ylim([0, bin_d])
        ax.set_zlim([0, bin_h])

        ax.set_box_aspect((bin_w, bin_d, bin_h)) 

        ax.view_init(azim=-120, elev=30)

        ax.xaxis.set_major_locator(MaxNLocator(nbins=3)) 
        ax.yaxis.set_major_locator(MaxNLocator(nbins=3))
        ax.zaxis.set_major_locator(MaxNLocator(nbins=4))
        
        # Draw items in the bin
        for item_id, item in bin_obj.items.items():
            color_to_use = empty_pallet_color
            if not item.empty:
                color_to_use = pallet_to_item_map.get(item.id, 'magenta')
            
            # Map item.position y to plot z, and item.position z to plot y
            plot_pos = (item.position[0], item.position[2], item.position[1])
            plot_cuboid(ax, plot_pos, item.placed_dimensions, color=color_to_use)


def create_animation(history: list, placed_item_sequence: list, manager: ASRSManager, plan_history: list, output_filename: str = "online.gif"):
    """
    Creates and saves a GIF animation of the ASRS system.
    """
    num_bins = len(manager.bins)
    ncols = num_bins
    nrows = 1
    
    fig, axs = plt.subplots(nrows, ncols, figsize=(30, 12), subplot_kw={'projection': '3d'})
    fig.subplots_adjust(
        left=0.05,    # 左邊界留白
        right=0.95,   # 右邊界留白
        bottom=0.05,  # 下邊界留白
        top=0.95,      # 上邊界留白 (留空間給主標題)
        wspace=0.05,   # 子圖之間的水平間距
        hspace=0.05   # 子圖之間的垂直間距
    )

    if num_bins == 1:
        axs = np.array([axs])

    # Hide unused subplots
    for i in range(num_bins, len(axs.flat)):
        axs.flat[i].axis('off')

    # --- Prepare colors ---
    item_ids = [item.id for item in placed_item_sequence if item is not None]
    colormap = plt.get_cmap('tab20', len(item_ids) if len(item_ids) > 0 else 1)
    item_colors_list = [colormap(i) for i in range(len(item_ids))]
    random.shuffle(item_colors_list)
    
    pallet_to_item_map = {}
    empty_pallet_color = 'lightblue'

    # --- Create Animation ---
    print("Generating animation... This may take a few moments.")
    ani = FuncAnimation(fig, update_all_bins, frames=len(history),
                        fargs=(history, placed_item_sequence, plan_history, manager, fig, axs, item_colors_list, pallet_to_item_map, empty_pallet_color),
                        interval=1500, repeat=False)

    # --- Save GIF ---
    try:
        # Using Pillow as the writer is a reliable way to save GIFs
        ani.save(output_filename, writer='pillow', dpi=80)
        print(f"Successfully saved animation to '{output_filename}'")
    except Exception as e:
        print(f"Error saving animation: {e}")
        print("Please make sure you have 'Pillow' installed (`pip install Pillow`).")
    
    plt.close(fig)