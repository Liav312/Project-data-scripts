import matplotlib.pyplot as plt

# Define the skeleton order and rows
MP15_SKELETON_ORDER = [
    "Head", "L_Shoulder", "R_Shoulder", "L_Elbow", "R_Elbow", "L_Wrist", "R_Wrist",
    "L_Hip", "R_Hip", "L_Knee", "R_Knee", "L_Ankle", "R_Ankle", "L_Foot", "R_Foot"
]
N_JOINTS_MP15 = 15
ROW_MP15 = {name: i for i, name in enumerate(MP15_SKELETON_ORDER)}

# Define the skeletal edges
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

# Define positions for each joint to represent a human skeleton
pos = {
    ROW_MP15["Head"]: (0, 10),
    ROW_MP15["L_Shoulder"]: (-2, 8),
    ROW_MP15["R_Shoulder"]: (2, 8),
    ROW_MP15["L_Elbow"]: (-3, 5),
    ROW_MP15["R_Elbow"]: (3, 5),
    ROW_MP15["L_Wrist"]: (-3, 2),
    ROW_MP15["R_Wrist"]: (3, 2),
    ROW_MP15["L_Hip"]: (-2, 0),
    ROW_MP15["R_Hip"]: (2, 0),
    ROW_MP15["L_Knee"]: (-2, -4),
    ROW_MP15["R_Knee"]: (2, -4),
    ROW_MP15["L_Ankle"]: (-2, -7),
    ROW_MP15["R_Ankle"]: (2, -7),
    ROW_MP15["L_Foot"]: (-3, -9),
    ROW_MP15["R_Foot"]: (3, -9)
}

# Create inverse mapping for node names
node_names = {i: name for name, i in ROW_MP15.items()}

# Create the plot
fig, ax = plt.subplots(figsize=(8, 12))

# Plot edges
for edge in skeletal_edges_mp15:
    x_vals = [pos[edge[0]][0], pos[edge[1]][0]]
    y_vals = [pos[edge[0]][1], pos[edge[1]][1]]
    ax.plot(x_vals, y_vals, 'k-')

# Plot nodes
for node, (x, y) in pos.items():
    ax.plot(x, y, 'bo', markersize=8)

# Add labels: number slightly above the node, name to the side based on L/R
for node, (x, y) in pos.items():
    # Node number
    ax.text(x+0.4, y + 0.15, str(node), ha='center', va='bottom', fontsize=12, color='red')
    
    # Node name
    name = node_names[node]
    if name.startswith('L_'):
        ax.text(x - 0.3, y, name, ha='right', va='center', fontsize=10)
    elif name.startswith('R_'):
        ax.text(x + 0.3, y, name, ha='left', va='center', fontsize=10)
    else:  # Head
        ax.text(x, y + 0.5, name, ha='center', va='bottom', fontsize=10)

# Set aspect ratio, limits, and remove axes for a cleaner look
ax.set_aspect('equal')
ax.set_xlim(-10, 10)
ax.set_ylim(-10, 12)
ax.axis('off')  # Turn off axes

plt.show()