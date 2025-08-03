#!/usr/bin/env python3
"""
parallel_skeleton2npy.py

Convert filtered NTU .skeleton files into .npy arrays of shape (T,17,3),
mapping original joint indices to new positions so that “original joint 4”
ends up in “new index 2,” etc., and preserving the original (x,y,z).

Usage:
    python parallel_skeleton2npy.py valid_list.txt /output/dir
"""
import os
import sys
import numpy as np
from concurrent.futures import ProcessPoolExecutor, as_completed
from functools import partial

# Map: original NTU joint index → new index in the 17-joint array
JOINT_MAP = {
     3:  2,   # Head           → new idx 2
     8:  6,   # Right shoulder → new idx 6
     4:  3,   # Left shoulder  → new idx 3
    20:  1,   # Spine          → new idx 1
     5:  4,   # Left elbow     → new idx 4
     9:  7,   # Right elbow    → new idx 7
    10:  8,   # Right wrist    → new idx 8
     7:  5,   # Left hand      → new idx 5
    16: 13,   # Right hip      → new idx 13
     0:  0,   # Base spine     → new idx 0
    12:  9,   # Left hip       → new idx 9
    17: 14,   # Right knee     → new idx 14
    13: 10,   # Left knee      → new idx 10
    19: 16,   # Right foot     → new idx 16
    18: 15,   # Right ankle    → new idx 15
    14: 11,   # Left ankle     → new idx 11
    15: 12,   # Left foot      → new idx 12
}


def convert_one(skel_path, out_dir):

    with open(skel_path, 'r') as f:
        n_frames = int(f.readline().strip())
        out = np.zeros((n_frames, len(JOINT_MAP), 3), dtype=np.float32)

        for fi in range(n_frames):
            _ = f.readline()                   # num_bodies
            _ = f.readline()                   # body header + lean + trackingState
            joint_count = int(f.readline().strip())

            for j in range(joint_count):
                parts = f.readline().split()
                x, y, z = map(float, parts[:3])
                if j in JOINT_MAP:
                    new_idx = JOINT_MAP[j]
                    out[fi, new_idx, :] = (x, y, z)
            # skip any remaining joints if joint_count > max key
            # (but our loop already reads all joint_count lines)

    base      = os.path.splitext(os.path.basename(skel_path))[0]
    out_path  = os.path.join(out_dir, base + '.npy')
    np.save(out_path, out)
    return out_path, out.shape

def main(list_file, out_dir, workers=None):
    os.makedirs(out_dir, exist_ok=True)
    with open(list_file, 'r') as lf:
        paths = [l.strip() for l in lf if l.strip()]

    workers = workers or os.cpu_count() or 4
    print(f"Converting {len(paths)} files with {workers} workers…")

    converter = partial(convert_one, out_dir=out_dir)
    with ProcessPoolExecutor(max_workers=workers) as exe:
        futures = {exe.submit(converter, p): p for p in paths}
        for i, fut in enumerate(as_completed(futures), 1):
            src = futures[fut]
            try:
                out_path, shape = fut.result()
                print(f"[{i}/{len(paths)}] {os.path.basename(src)} → {shape}")
            except Exception as e:
                print(f"[ERROR] {src}: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
