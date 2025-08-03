import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation

# ---------------------------------------------------------
# 1) Load Data
# ---------------------------------------------------------
#filepath = "converted_skeleton_npy/S032C002P043R002A074.npy"  # change to your file
filepath = "emb_suemd_viconYZ_swap/S1A1D1R2.npy"  # change to your file
data = np.load(filepath)

T = data.shape[0]  # number of frames
print("Data shape:", data.shape)  # e.g. (146, 17, 3)
print(np.max(data), np.min(data))  # check value range
# ---------------------------------------------------------
# 2) Skeleton connectivity
# ---------------------------------------------------------
skeletal_edges = [
    (0,1), (1,2),
    (1,3), (3,4), (4,5),
    (1,6), (6,7), (7,8),
    (0,9), (9,10), (10,11), (11,12),
    (0,13), (13,14), (14,15), (15,16)
]

# ---------------------------------------------------------
# 3) Setup Figure and Axes
# ---------------------------------------------------------
fig = plt.figure(figsize=(7,7))
ax = fig.add_subplot(111, projection='3d')

# We create empty objects that we'll update later
scatter_plot = ax.scatter([], [], [], c='b', s=30)
lines = []
for _ in range(len(skeletal_edges)):
    line, = ax.plot([], [], [], c='r')
    lines.append(line)

ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_zlabel("Z")

ax.set_xlim3d([-4, 4])
ax.set_ylim3d([-1, 1])
ax.set_zlim3d([2, 5])


# ---------------------------------------------------------
# 4) Define the Update Function
# ---------------------------------------------------------
def update(frame_idx):
    """
    This function updates the scatter points and lines
    for frame 'frame_idx'.
    """
    coords = data[frame_idx]  # shape (17, 3)
    x_vals = coords[:, 0]
    y_vals = coords[:, 1]
    z_vals = coords[:, 2]

    # Update scatter (this is a bit hacky: we remove and re-draw)
    scatter_plot._offsets3d = (x_vals, y_vals, z_vals)

    # Update each line
    for line, (j1, j2) in zip(lines, skeletal_edges):
        x_pair = [x_vals[j1], x_vals[j2]]
        y_pair = [y_vals[j1], y_vals[j2]]
        z_pair = [z_vals[j1], z_vals[j2]]
        line.set_data_3d(x_pair, y_pair, z_pair)

    ax.set_title(f"Frame {frame_idx}/{T-1}")
    return [scatter_plot] + lines

# ---------------------------------------------------------
# 5) Create the Animation
# ---------------------------------------------------------
anim = FuncAnimation(
    fig,
    update,
    frames=range(T),       # from 0 to T-1
    interval=50,           # delay between frames in milliseconds
    blit=False,            # or True, but need to return artists properly
    repeat=True
)

plt.show()
