# scripts/convert_ntu17_to_mp15.py

import numpy as np
from pathlib import Path
import argparse
from tqdm import tqdm
import multiprocessing # For using multiple cores
import os # For getting CPU count

# Import constants for the original NTU 17-joint format
try:
    from constants_ntu import NTU_17_JOINTS_ORDER, ROW_NTU
    if len(NTU_17_JOINTS_ORDER) != 17:
        print(f"Warning: NTU_17_JOINTS_ORDER in constants_ntu.py has {len(NTU_17_JOINTS_ORDER)} elements, expected 17.")
except ImportError:
    print("ERROR: src.utils.constants_ntu.py not found or incorrectly structured.")
    print("Please ensure NTU_17_JOINTS_ORDER (list of 17 joint names) and ROW_NTU (dict name:index) are defined.")
    exit()

# Import constants for the target MediaPipe-compatible 15-joint format
try:
    from constants_mp15 import MP15_SKELETON_ORDER, ROW_MP15, N_JOINTS_MP15
    if N_JOINTS_MP15 != 15:
        print(f"Warning: N_JOINTS_MP15 in constants_mp15.py is {N_JOINTS_MP15}, expected 15.")
except ImportError:
    print("ERROR: src.utils.constants_mp15.py not found or incorrectly structured.")
    exit()


# --- Global variable for mapping ---
# This is necessary for multiprocessing if the mapping is complex and generated once.
# For simple mappings, it could be passed, but this is cleaner for helper functions.
# It will be initialized in the main execution block.
NTU17_TO_MP15_MAPPING = None

def get_ntu17_to_mp15_mapping_global():
    """
    Initializes and returns the global mapping.
    This function is called by worker processes if they need the mapping.
    """
    global NTU17_TO_MP15_MAPPING
    if NTU17_TO_MP15_MAPPING is None:
        mapping = {}
        for mp15_name in MP15_SKELETON_ORDER:
            if mp15_name in ROW_NTU:
                mapping[mp15_name] = mp15_name
            else:
                # This should not be hit if constants are aligned as discussed
                raise ValueError(
                    f"MP15 joint '{mp15_name}' cannot be directly mapped. "
                    f"Ensure its corresponding name exists in NTU_17_JOINTS_ORDER (constants_ntu.py)"
                )
        # Validate
        for mp15_name_target, ntu_source_name_in_map in mapping.items():
            if ntu_source_name_in_map not in ROW_NTU:
                raise ValueError(
                    f"Consistency error: Source NTU joint '{ntu_source_name_in_map}' (for MP15 '{mp15_name_target}') "
                    f"is not a key in ROW_NTU. Check constants_ntu.py."
                )
        NTU17_TO_MP15_MAPPING = mapping
    return NTU17_TO_MP15_MAPPING


def convert_single_ntu17_file_to_mp15(ntu17_npy_path: Path, output_mp15_dir: Path) -> tuple[Path, bool, str | None]:
    """
    Converts a single (T, 17, 3) NTU npy file to (T, 15, 3) MP15 format and saves it.
    Returns: (input_path, success_status, error_message_if_any)
    """
    mapping = get_ntu17_to_mp15_mapping_global() # Get the globally initialized mapping

    try:
        ntu17_data = np.load(ntu17_npy_path)
    except Exception as e:
        return (ntu17_npy_path, False, f"Error loading: {e}")

    if ntu17_data.ndim != 3 or ntu17_data.shape[1] != len(NTU_17_JOINTS_ORDER) or ntu17_data.shape[2] != 3:
        return (ntu17_npy_path, False, f"Unexpected shape {ntu17_data.shape}")

    n_frames = ntu17_data.shape[0]
    mp15_data = np.zeros((n_frames, N_JOINTS_MP15, 3), dtype=np.float32)

    for mp15_idx, mp15_target_name in enumerate(MP15_SKELETON_ORDER):
        ntu_source_name = mapping[mp15_target_name]
        ntu_source_idx = ROW_NTU[ntu_source_name]
        mp15_data[:, mp15_idx, :] = ntu17_data[:, ntu_source_idx, [0, 2, 1]] / 1000

    output_file_path = output_mp15_dir / ntu17_npy_path.name
    try:
        np.save(output_file_path, mp15_data)
        return (ntu17_npy_path, True, None)
    except Exception as e:
        return (ntu17_npy_path, False, f"Error saving {output_file_path}: {e}")


# Helper for multiprocessing pool's map function
def worker_process_file(file_path_and_output_dir_tuple):
    """ Unpacks arguments and calls the conversion function. """
    file_path, output_dir = file_path_and_output_dir_tuple
    return convert_single_ntu17_file_to_mp15(file_path, output_dir)


def main():
    parser = argparse.ArgumentParser(
        description="Convert NTU 17-joint .npy files to MediaPipe-compatible 15-joint .npy files using multiple cores."
    )
    parser.add_argument(
        "--ntu17_dir", type=str, required=True, help="Directory containing original NTU 17-joint .npy files."
    )
    parser.add_argument(
        "--output_mp15_dir", type=str, required=True, help="Directory to save converted MP15-joint .npy files."
    )
    parser.add_argument(
        "--num_cores", type=int, default=32, help="Number of CPU cores to use. Defaults to os.cpu_count()."
    )
    args = parser.parse_args()

    ntu17_dir = Path(args.ntu17_dir)
    output_mp15_dir = Path(args.output_mp15_dir)
    output_mp15_dir.mkdir(parents=True, exist_ok=True)

    if not ntu17_dir.is_dir():
        print(f"Error: Input directory '{ntu17_dir}' does not exist.")
        return

    # Initialize the global mapping ONCE in the main process.
    # Child processes created by the pool will inherit/re-initialize it via get_ntu17_to_mp15_mapping_global().
    try:
        get_ntu17_to_mp15_mapping_global() # Initializes NTU17_TO_MP15_MAPPING
        print("Using the following NTU17 to MP15 mapping (MP15 Target Name <-- NTU Source Name [Original NTU Index]):")
        for mp15_name, ntu_name in NTU17_TO_MP15_MAPPING.items(): # Access the initialized global
            print(f"  MP15 '{mp15_name}' <-- NTU '{ntu_name}' [index {ROW_NTU.get(ntu_name, 'N/A')}]")
    except ValueError as e:
        print(f"Error in joint mapping: {e}")
        return

    original_npy_files = sorted(list(ntu17_dir.glob("*.npy")))
    if not original_npy_files:
        print(f"No .npy files found in {ntu17_dir}")
        return

    print(f"Found {len(original_npy_files)} .npy files to process.")

    num_cores_to_use = args.num_cores if args.num_cores else os.cpu_count()
    if num_cores_to_use is None: # os.cpu_count() might return None
        num_cores_to_use = 1
        print("Could not determine CPU count, defaulting to 1 core.")
    else:
        print(f"Using {num_cores_to_use} CPU cores for conversion.")

    # Prepare arguments for worker_process_file: a list of tuples
    tasks = [(file_path, output_mp15_dir) for file_path in original_npy_files]

    conversion_errors = 0
    successful_conversions = 0

    # Using multiprocessing.Pool
    # The `with` statement ensures the pool is properly closed.
    with multiprocessing.Pool(processes=num_cores_to_use) as pool:
        # Use tqdm with pool.imap_unordered for progress bar with multiprocessing
        # imap_unordered is good for tasks that don't need to maintain order and might finish at different times.
        results = list(tqdm(pool.imap_unordered(worker_process_file, tasks), total=len(tasks), desc="Converting files"))

    for input_path, success, error_msg in results:
        if success:
            successful_conversions += 1
        else:
            conversion_errors += 1
            print(f"Failed to process {input_path.name}: {error_msg}")
            
    print(f"\nConversion complete.")
    print(f"Successfully converted: {successful_conversions} files.")
    print(f"Errors/Skipped: {conversion_errors} files.")
    print(f"Converted files are in {output_mp15_dir}")

if __name__ == "__main__":
    # Ensure your constants_*.py files are correctly defined in the src/utils directory.
    main()