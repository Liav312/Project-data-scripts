import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation
import sys
import os

# --- Add project root to sys.path for imports ---
# Assuming this script (test_mp15.py) is in a directory like 'scripts/'
# and 'src/' is a sibling directory.
# If test_mp15.py is in the project root, change '..' to '.'
try:
    # Calculate the project root directory dynamically
    # Assuming the script is in project_root/scripts/ or project_root/
    # If in project_root/scripts/, then dirname is 'scripts', parent is project_root
    # If in project_root/, then dirname is project_root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = script_dir # Default if script is in root
    # Check if 'src' is a subdir of current script_dir's parent (common structure)
    if os.path.isdir(os.path.join(os.path.dirname(script_dir), "src")):
         project_root = os.path.dirname(script_dir)
    elif not os.path.isdir(os.path.join(script_dir, "src")): # if src is not in current dir
        # Try one level up if common 'scripts' subdir structure
        potential_root = os.path.abspath(os.path.join(script_dir, '..'))
        if os.path.isdir(os.path.join(potential_root, "src")):
            project_root = potential_root

    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    print(f"Attempting to use project root: {project_root}")
except NameError: # __file__ is not defined (e.g. in interactive interpreter)
    print("Warning: Could not dynamically set project root. Imports might fail.")
    pass


# Attempt to import MP15 constants
try:
    from constants_mp15 import MP15_SKELETON_ORDER, ROW_MP15, N_JOINTS_MP15
    print(f"Successfully imported MP15 constants from src.utils. Using {N_JOINTS_MP15} joints.")
except ImportError as e:
    print(f"Warning: Could not import MP15 constants from src.utils (Error: {e}). Using fallback definitions.")
    MP15_SKELETON_ORDER = [ # Fallback definition
        "Head", "L_Shoulder", "R_Shoulder", "L_Elbow", "R_Elbow", "L_Wrist", "R_Wrist",
        "L_Hip", "R_Hip", "L_Knee", "R_Knee", "L_Ankle", "R_Ankle", "L_Foot", "R_Foot"
    ]
    N_JOINTS_MP15 = 15
    ROW_MP15 = {name: i for i, name in enumerate(MP15_SKELETON_ORDER)}

# ---------------------------------------------------------
# 1) Load Data
# ---------------------------------------------------------
# IMPORTANT: Change this filepath to point to one of your CONVERTED MP15 .npy files
# filepath = "emb_skeleton_data/S032C002P043R002A074.npy"  # change to your file
filepath = "emb_suemd_data/S1A1D1R2.npy"  # change to your file
# For testing, ensure this path is correct relative to where you RUN the script,
# OR use an absolute path.
# If running from project root: filepath = "output_mp15_dir/your_file.npy"

try:
    data = np.load(filepath)
except FileNotFoundError:
    print(f"Error: File not found at '{filepath}'")
    print("Please ensure the filepath is correct and the file exists.")
    print(f"Current working directory: {os.getcwd()}")
    exit()

if data.ndim != 3 or data.shape[1] != N_JOINTS_MP15 or data.shape[2] != 3:
    print(f"Error: Data shape is {data.shape}, but expected (T, {N_JOINTS_MP15}, 3).")
    print(f"Please ensure you are loading an MP15 ({N_JOINTS_MP15}-joint) .npy file.")
    exit()

T = data.shape[0]
print(f"Data loaded from: {filepath}")
print("Data shape:", data.shape)
print("Value range: min =", np.min(data), "max =", np.max(data)) # Min/Max from your output: -110 to 1717

# ---------------------------------------------------------
# 2) Skeleton connectivity for MP15
# ---------------------------------------------------------
skeletal_edges_mp15 = [
    (ROW_MP15["Head"], ROW_MP15["L_Shoulder"]), (ROW_MP15["Head"], ROW_MP15["R_Shoulder"]),
    (ROW_MP15["L_Shoulder"], ROW_MP15["R_Shoulder"]),
    (ROW_MP15["L_Shoulder"], ROW_MP15["L_Hip"]), (ROW_MP15["R_Shoulder"], ROW_MP15["R_Hip"]),
    (ROW_MP15["L_Hip"], ROW_MP15["R_Hip"]),
    (ROW_MP15["L_Shoulder"], ROW_MP15["L_Elbow"]), (ROW_MP15["L_Elbow"], ROW_MP15["L_Wrist"]),
    (ROW_MP15["R_Shoulder"], ROW_MP15["R_Elbow"]), (ROW_MP15["R_Elbow"], ROW_MP15["R_Wrist"]),
    (ROW_MP15["L_Hip"], ROW_MP15["L_Knee"]), (ROW_MP15["L_Knee"], ROW_MP15["L_Ankle"]),
    (ROW_MP15["L_Ankle"], ROW_MP15["L_Foot"]),
    (ROW_MP15["R_Hip"], ROW_MP15["R_Knee"]), (ROW_MP15["R_Knee"], ROW_MP15["R_Ankle"]),
    (ROW_MP15["R_Ankle"], ROW_MP15["R_Foot"]),
]

# ---------------------------------------------------------
# 3) Setup Figure and Axes
# ---------------------------------------------------------
fig = plt.figure(figsize=(8, 8))
ax = fig.add_subplot(111, projection='3d')

scatter_plot = ax.scatter([], [], [], c='blue', s=40, alpha=0.7)
lines = []
for _ in range(len(skeletal_edges_mp15)):
    line, = ax.plot([], [], [], c='red', linewidth=1.5)
    lines.append(line)

ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_zlabel("Z")

# --- Adjust Axis Limits BASED ON YOUR DATA RANGE (-110 to 1717) ---
# The data range "min = -110.652115 max = 1717.8536" suggests this is NOT
# preprocessed (centered, scaled, Z-scored) data yet. These are likely raw mm or similar.
# Set limits that encompass this range, or calculate dynamically.
# Let's try dynamic calculation for now, then you can fix them if you prefer.

all_x = data[..., 0].flatten()
all_y = data[..., 2].flatten()
all_z = data[..., 1].flatten()
x_min, x_max = np.min(all_x) - 1, np.max(all_x) + 1 # Add some padding
y_min, y_max = np.min(all_y) - 1, np.max(all_y) + 1
z_min, z_max = np.min(all_z) - 1, np.max(all_z) + 1

# Ensure the ranges are somewhat proportional or set a common scale
max_range = np.array([x_max-x_min, y_max-y_min, z_max-z_min]).max() / 2.0
mid_x = (x_max+x_min) * 0.5
mid_y = (y_max+y_min) * 0.5
mid_z = (z_max+z_min) * 0.5

ax.set_xlim(mid_x - max_range, mid_x + max_range)
ax.set_ylim(mid_y - max_range, mid_y + max_range)
ax.set_zlim(mid_z - max_range, mid_z + max_range)


print(f"Axis limits: X=({mid_x - max_range:.1f}, {mid_x + max_range:.1f}), "
      f"Y=({mid_y - max_range:.1f}, {mid_y + max_range:.1f}), "
      f"Z=({mid_z - max_range:.1f}, {mid_z + max_range:.1f})")


ax.view_init(elev=20., azim=-70)

# ---------------------------------------------------------
# 4) Define the Update Function
# ---------------------------------------------------------
def update(frame_idx):
    coords = data[frame_idx]
    x_vals = coords[:, 0]
    y_vals = coords[:, 1]
    z_vals = coords[:, 2]

    scatter_plot._offsets3d = (x_vals, y_vals, z_vals) # Corrected scatter update

    for line, (j1_idx, j2_idx) in zip(lines, skeletal_edges_mp15):
        line.set_data([x_vals[j1_idx], x_vals[j2_idx]], [y_vals[j1_idx], y_vals[j2_idx]])
        line.set_3d_properties([z_vals[j1_idx], z_vals[j2_idx]])

    ax.set_title(f"MP15 Skeleton - Frame {frame_idx}/{T-1}")
    return [scatter_plot] + lines

# ---------------------------------------------------------
# 5) Create the Animation
# ---------------------------------------------------------
anim = FuncAnimation(
    fig,
    update,
    frames=range(T),
    interval=33,
    blit=True, # Keep blit=True, the scatter_plot._offsets3d often works well with it
    repeat=False
)

plt.tight_layout()
plt.show()