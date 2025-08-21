import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MaxNLocator

def plot_cuboid_with_cuts(x_range, y_range, z_range, num_yz_cuts=3, num_xz_cuts=2):
    """
    Draws a cuboid in 3D space with optional cuts along the YZ and XZ planes.

    :param x_range: Tuple (x_min, x_max) for the X dimension.
    :param y_range: Tuple (y_min, y_max) for the Y dimension.
    :param z_range: Tuple (z_min, z_max) for the Z dimension.
    :param num_yz_cuts: Number of cuts along the YZ plane (default is 3).
    :param num_xz_cuts: Number of cuts along the XZ plane (default is 2).

    :return: None
    """
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    x_min, x_max = x_range
    y_min, y_max = y_range
    z_min, z_max = z_range

    # define the vertices of the cuboid
    vertices = np.array([
        (x_min, y_min, z_min), (x_max, y_min, z_min),
        (x_max, y_max, z_min), (x_min, y_max, z_min),
        (x_min, y_min, z_max), (x_max, y_min, z_max),
        (x_max, y_max, z_max), (x_min, y_max, z_max)
    ])

    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0),
        (4, 5), (5, 6), (6, 7), (7, 4),
        (0, 4), (1, 5), (2, 6), (3, 7)
    ]

    # draw the cuboid
    for i, j in edges:
        ax.plot3D(*zip(vertices.take(i, axis=0), vertices.take(j, axis=0)), color='b')

    # draw YZ plane cuts
    if num_yz_cuts > 0:
        cut_x_values = np.linspace(x_min, x_max, num_yz_cuts + 2)[1:-1]
        for x_cut in cut_x_values:
            ax.plot([x_cut, x_cut], [y_min, y_max], [z_min, z_min], color='r', linestyle='--')
            ax.plot([x_cut, x_cut], [y_min, y_max], [z_max, z_max], color='r', linestyle='--')
            ax.plot([x_cut, x_cut], [y_min, y_min], [z_min, z_max], color='r', linestyle='--')
            ax.plot([x_cut, x_cut], [y_max, y_max], [z_min, z_max], color='r', linestyle='--')

    # if num_xz_cuts > 0:
    #     cut_y_values = np.linspace(y_min, y_max, num_xz_cuts + 2)[1:-1]
    #     for y_cut in cut_y_values:
    #         ax.plot([x_min, x_max], [y_cut, y_cut], [z_min, z_min], color='g', linestyle='--')
    #         ax.plot([x_min, x_max], [y_cut, y_cut], [z_max, z_max], color='g', linestyle='--')
    #         ax.plot([x_min, x_min], [y_cut, y_cut], [z_min, z_max], color='g', linestyle='--')
    #         ax.plot([x_max, x_max], [y_cut, y_cut], [z_min, z_max], color='g', linestyle='--')

    ax.set_xlabel('X', loc="right")
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.set_zlim(z_min, z_max)

    x_len = x_max - x_min
    y_len = y_max - y_min
    z_len = z_max - z_min

    max_len = max(x_len, y_len, z_len)
    ax.set_box_aspect([x_len / max_len, y_len / max_len, z_len / max_len])
    # ax.set_box_aspect([x_len / min_len, y_len / min_len, z_len / min_len])
    ax.yaxis.set_major_locator(MaxNLocator(nbins=4))
    ax.zaxis.set_major_locator(MaxNLocator(nbins=5))

    plt.show()

# Example usage
x_min, x_max = 0, 450
y_min, y_max = 0, 50
z_min, z_max = 0, 200

plot_cuboid_with_cuts((x_min, x_max), (y_min, y_max), (z_min, z_max), num_yz_cuts=8, num_xz_cuts=0)