#!/usr/bin/env python3
import os
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed

# joints to check
JOINT_IDS = [3, 8, 4, 20, 5, 9, 10, 7, 16, 0, 12, 17, 13, 19, 18, 14, 15]

def file_passes(path):
    """
    Return True if `path` meets all criteria on every frame; False otherwise.
    """
    try:
        with open(path, 'r') as f:
            n_frames = int(f.readline().strip())
            for _ in range(n_frames):
                if int(f.readline().strip()) != 1:       # num_bodies
                    return False
                parts = f.readline().split()           # body header + lean + tracking
                if len(parts) < 10 or int(parts[1]) != 0 or int(parts[6]) != 0:
                    return False
                # skip jointCount line, then read jointCount
                joint_count = int(f.readline().strip())
                if joint_count < 17:
                    return False
                # per-joint: 11 floats + 1 int at end
                for j in range(joint_count):
                    line = f.readline().split()
                    if j in JOINT_IDS and int(line[11]) not in (1,2):
                        return False
        return True
    except:
        return False  # any parse error → reject

def gather_skeleton_files(root_dir):
    for root, _, files in os.walk(root_dir):
        for fn in files:
            if fn.endswith('.skeleton'):
                yield os.path.join(root, fn)

def main(input_dir, output_file):
    all_files = list(gather_skeleton_files(input_dir))
    total = len(all_files)
    valid = []

    # Use all available CPU cores
    with ProcessPoolExecutor() as exe:
        futures = {exe.submit(file_passes, p): p for p in all_files}
        for i, fut in enumerate(as_completed(futures), 1):
            path = futures[fut]
            if fut.result():
                valid.append(path)
            # progress update every 1000 files
            if i % 1000 == 0:
                print(f"Processed {i}/{total} files…", end='\r')

    # Write results
    with open(output_file, 'w') as out:
        out.write('\n'.join(valid))

    print(f"\n✅ Scanned {total} files, found {len(valid)} valid → {output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python parallel_filter.py <input_dir> <output_file>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
