# src/utils/constants_mp15.py

MP15_SKELETON_ORDER = [
    "Head",          
    "L_Shoulder",    
    "R_Shoulder",    
    "L_Elbow",     
    "R_Elbow",       
    "L_Wrist",       
    "R_Wrist",       
    "L_Hip",         
    "R_Hip",         
    "L_Knee",        
    "R_Knee",       
    "L_Ankle",       
    "R_Ankle",      
    "L_Foot",        
    "R_Foot"         
]

N_JOINTS_MP15 = len(MP15_SKELETON_ORDER) # Should be 15

ROW_MP15 = {name: i for i, name in enumerate(MP15_SKELETON_ORDER)}

# Indices for preprocessing, relative to MP15_SKELETON_ORDER
# For centering, we'll use the average of hips, as there's no direct 'Pelvis' or 'SpineBase'
PELVIS_AVG_MP15 = (ROW_MP15["L_Hip"], ROW_MP15["R_Hip"])

# For yaw alignment:
HIP_LEFT_MP15 = ROW_MP15["L_Hip"]
HIP_RIGHT_MP15 = ROW_MP15["R_Hip"]

# For scale normalization (torso proxy):
SHOULDER_LEFT_MP15 = ROW_MP15["L_Shoulder"]
SHOULDER_RIGHT_MP15 = ROW_MP15["R_Shoulder"]
# HipLeft and HipRight for MP15 already defined above