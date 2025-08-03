# src/utils/constants_ntu.py

# Defines the joint order and names for your original 17-joint NTU .npy files.
# This order MUST exactly match the structure of your (..., 17, 3) .npy files.
# Names are chosen to align with MP15 names where a direct correspondence is assumed.
# VERIFY THE SEMANTIC MEANING OF "NTU_L_Wrist_Source" (HandLeft).

NTU_17_JOINTS_ORDER = [
    "NTU_SpineBase",      # 0 - NTU specific
    "NTU_SpineShoulder",  # 1 - NTU specific
    "Head",               # 2 - Corresponds to NTU "Head", maps to MP15 "Nose"
    "L_Shoulder",         # 3 - Corresponds to NTU "ShoulderLeft"
    "L_Elbow",            # 4 - Corresponds to NTU "ElbowLeft"
    "L_Wrist", # 5 - Corresponds to NTU "HandLeft". ASSUMED to map to MP15 "L_Wrist". VERIFY THIS.
    "R_Shoulder",         # 6 - Corresponds to NTU "ShoulderRight"
    "R_Elbow",            # 7 - Corresponds to NTU "ElbowRight"
    "R_Wrist",            # 8 - Corresponds to NTU "WristRight"
    "L_Hip",              # 9 - Corresponds to NTU "HipLeft"
    "L_Knee",             # 10 - Corresponds to NTU "KneeLeft"
    "L_Ankle",            # 11 - Corresponds to NTU "AnkleLeft"
    "L_Foot",             # 12 - Corresponds to NTU "FootLeft"
    "R_Hip",              # 13 - Corresponds to NTU "HipRight"
    "R_Knee",             # 14 - Corresponds to NTU "KneeRight"
    "R_Ankle",            # 15 - Corresponds to NTU "AnkleRight"
    "R_Foot"              # 16 - Corresponds to NTU "FootRight"
]

N_JOINTS_NTU17 = len(NTU_17_JOINTS_ORDER) # Should be 17

# Mapping from joint name to index for easier access in conversion script
ROW_NTU = {name: i for i, name in enumerate(NTU_17_JOINTS_ORDER)}

