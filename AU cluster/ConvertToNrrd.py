import os
import sys
import glob
import csv
import tifffile
import nrrd
import numpy as np

def load_metadata_csv(csv_path):
    """Load voxel spacing metadata from CSV file."""
    metadata = {}
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            filename = row['filename']
            # Store spacing as (Z, Y, X) to match the resampling function
            metadata[filename] = np.array([
                float(row['voxel_depth']),
                float(row['voxel_height']),
                float(row['voxel_width'])
            ], dtype=float)
    return metadata

def load_tif(path):
    """Load TIF file and return data with spacing."""
    data = tifffile.imread(path)
    # TIF data is typically in (Z, Y, X) order
    return data.astype(np.float32)

def save_nrrd(data, voxel_spacing, out_path):
    # nibabel prefers data in (X, Y, Z) with affine describing voxel sizes.
    # Our data is often (Z, Y, X) from nrrd; we need to reorder.
    # We'll convert from (Z,Y,X) -> (X,Y,Z) for nifti array, and set affine accordingly.
    header = {'spacings': voxel_spacing}
    nrrd.write(out_path,np.flip(np.transpose(data, (2,1,0)),axis=-1),header,compression_level=1)
    print("Saved Nrrd:", out_path)

def convert_one(tif_path, out_path, spacing):
    data = load_tif(tif_path)
    print("Loaded:", tif_path, "shape:", data.shape, "spacing (Z,Y,X):", spacing)
    save_nrrd(data, spacing, out_path)


Folder='/faststorage/project/Inflammation/Brain_reg/'
tif_files=glob.glob(os.path.join(Folder,'3Dtif','*.tif'))



Folder = os.path.abspath(Folder)
if not tif_files:
    print("No _pERK.tif or _tERK.tif files found in", Folder)
    sys.exit(1)

# Load metadata CSV
#metadata_csv = os.path.join(Folder, "voxel_spacing_metadata.txt")
metadata_csv = os.path.join(Folder,'3Dtif', "voxel_spacing_metadata.txt")
if not os.path.exists(metadata_csv):
    print("Error: voxel_spacing_metadata.txt not found in", Folder)
    sys.exit(1)

metadata = load_metadata_csv(metadata_csv)
print("Loaded metadata for", len(metadata), "files")

# Create output directory `nii.gz` in the script's Folder (project root) if it doesn't exist
script_dir = os.path.dirname(os.path.abspath(__file__))
out_dir = os.path.join(Folder, "nrrd")
os.makedirs(out_dir, exist_ok=True)
print("Output directory:", out_dir)

for p in tif_files:
    basename = os.path.basename(p)
    # Extract original filename (without _pERK or _tERK suffix)
    if "_pERK.tif" in basename:
        orig_name = basename.replace("_pERK.tif", "")
    elif "_tERK.tif" in basename:
        orig_name = basename.replace("_tERK.tif", "")
    else:
        continue
    # Get spacing from metadata
    if orig_name not in metadata:
        print(f"Warning: No metadata found for {orig_name}, skipping {basename}")
        continue
    spacing = metadata[orig_name]
    out_name = basename.replace(".tif", ".nrrd")
    out = os.path.join(out_dir, out_name)
    convert_one(p, out, spacing)
