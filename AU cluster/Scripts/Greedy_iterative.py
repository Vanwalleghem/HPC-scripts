import csv
import glob
import os
import re
import sys
import subprocess

import nibabel as nib
import natsort
import numpy as np
import tifffile

from scipy.ndimage import uniform_filter

MAX_PASSES = 8
PATIENCE = 2
MIN_GAIN = 0.005


# -------------------------------------------------------------------------
# Utilities
# -------------------------------------------------------------------------

def run_command(cmd):
    print(cmd)
    subprocess.run(cmd, shell=True, check=True)


def is_file_empty(path):
    return (not os.path.exists(path)) or os.path.getsize(path) == 0


def get_base_name(filename):
    return re.sub(r"_Warp\d+\.nii\.gz$", "", filename)


# -------------------------------------------------------------------------
# Registration quality metric
# -------------------------------------------------------------------------


def compute_wncc_fast(
    img1,
    img2,
    mask=None,
    window_size=(32, 32, 4),
):
    img1 = np.asarray(img1, dtype=np.float64)
    img2 = np.asarray(img2, dtype=np.float64)

    if img1.shape != img2.shape:
        raise ValueError(
            f"Image shape mismatch: {img1.shape} vs {img2.shape}"
        )

    if not np.isfinite(img1).all() or not np.isfinite(img2).all():
        raise ValueError("Images contain NaN or infinite values")

    if mask is None:
        mask = np.ones(img1.shape, dtype=bool)
    else:
        mask = np.asarray(mask) > 0

    if mask.shape != img1.shape:
        raise ValueError(
            f"Mask shape mismatch: {mask.shape} vs {img1.shape}"
        )

    if not mask.any():
        raise ValueError("Mask contains no foreground voxels")

    # Global centering does not change local correlation, but retain
    # it to minimize changes to the existing implementation.
    img1 = img1 - img1.mean()
    img2 = img2 - img2.mean()

    m1 = uniform_filter(img1, size=window_size)
    m2 = uniform_filter(img2, size=window_size)

    m11 = uniform_filter(img1 * img1, size=window_size)
    m22 = uniform_filter(img2 * img2, size=window_size)
    m12 = uniform_filter(img1 * img2, size=window_size)

    cov = m12 - m1 * m2
    var1 = m11 - m1 * m1
    var2 = m22 - m2 * m2

    valid = (
        mask
        & (var1 > 1e-6)
        & (var2 > 1e-6)
        & np.isfinite(cov)
        & np.isfinite(var1)
        & np.isfinite(var2)
    )

    if not valid.any():
        raise ValueError(
            "No valid voxels available for WNCC calculation"
        )

    wncc = cov[valid] / np.sqrt(
        np.maximum(var1[valid] * var2[valid], 1e-12)
    )

    wncc = np.clip(wncc, -1.0, 1.0)

    return float(np.mean(wncc))



# -------------------------------------------------------------------------
# Template selection
# -------------------------------------------------------------------------

def FindTemplate(folder, n_frames=50):

    reg_dir = os.path.join(folder, "3Dreg")

    files = natsort.natsorted(
        glob.glob(os.path.join(reg_dir, "*_time*.tif"))
    )

    if not files:
        files = natsort.natsorted(
            glob.glob(os.path.join(reg_dir, "*.tif"))
        )

    filtered = []

    for f in files:

        name = os.path.basename(f).lower()

        if "template" in name:
            continue

        if "_warp" in name:
            continue

        filtered.append(f)

    files = filtered[:n_frames]

    if len(files) < 2:
        raise RuntimeError(
            f"Need at least 2 TIFFs in {reg_dir}"
        )

    scores = np.zeros(len(files), dtype=np.float32)

    prev = None

    for i, f in enumerate(files):

        vol = tifffile.imread(f)

        if prev is not None:

            diff = float(
                np.percentile(
                    np.abs(
                        vol.astype(np.float32)
                        - prev.astype(np.float32)
                    ),
                    95
                )
            )

            scores[i] = max(scores[i], diff)
            scores[i - 1] = max(scores[i - 1], diff)

        prev = vol

    return files[int(np.argmin(scores))]


# -------------------------------------------------------------------------
# Initial registration
# -------------------------------------------------------------------------

def Register_single_image(Mov_name,
                          template_name,
                          mask_name):

    output_name = Mov_name.replace(".tif", "_orig")

    affine_name = Mov_name.replace(
        ".tif",
        "_orig_affine.mat"
    )

    warp1 = Mov_name + "_Warp1.nii.gz"

    if is_file_empty(affine_name):

        cmd = (
            "greedy -d 3 -a "
            f"-o {affine_name} "
            f"-i {template_name} {Mov_name} "
            "-n 300x200x150 "
            "-e 0.25 "
            "-ia-identity "
            "-m NCC 3x3x2"
        )

        run_command(cmd)

    if is_file_empty(output_name + ".nii.gz"):

        cmd = (
            "greedy -d 3 "
            "-s 1.8vox 1vox "
            f"-o {output_name}.nii.gz "
            f"-i {template_name} {Mov_name} "
            f"-gm {mask_name} "
            f"-mm {mask_name} "
            f"-it {affine_name} "
            "-sv "
            "-n 300x150x80 "
            "-e 0.5 "
            "-m NCC 3x3x2"
        )

        run_command(cmd)

    if is_file_empty(warp1):

        cmd = (
            "greedy -d 3 "
            f"-rf {template_name} "
            f"-rm {Mov_name} {warp1} "
            f"-r {output_name}.nii.gz {affine_name}"
        )

        run_command(cmd)

    return warp1


# -------------------------------------------------------------------------
# Additional pass
# -------------------------------------------------------------------------

def RegisterPass(Mov_name,
                 template_name,
                 mask_name,
                 pass_number):

    base = get_base_name(Mov_name)

    field = f"{base}_orig{pass_number}.nii.gz"
    warped = f"{base}_Warp{pass_number}.nii.gz"

    if is_file_empty(field):

        cmd = (
            "greedy -d 3 -float "
            f"-o {field} "
            f"-i {template_name} {Mov_name} "
            f"-gm {mask_name} "
            f"-mm {mask_name} "
            "-sv "
            "-n 300x150x50 "
            "-e 0.25 "
            "-m NCC 3x3x2"
        )

        run_command(cmd)

    if is_file_empty(warped):

        cmd = (
            "greedy -d 3 "
            f"-rf {template_name} "
            f"-rm {Mov_name} {warped} "
            f"-r {field}"
        )

        run_command(cmd)

    return warped


# -------------------------------------------------------------------------
# Adaptive optimisation
# -------------------------------------------------------------------------


def AdaptiveRegistration(
    first_warp_file,
    template,
    mask,
    template_name,
    mask_name,
    csv_file,
):
    best_file = first_warp_file
    best_score = -np.inf

    previous_score = None
    current_file = first_warp_file
    stale_passes = 0
    stop_reason = "maximum_passes_reached"
    best_pass = None

    with open(csv_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "pass",
            "wncc",
            "gain",
            "best_wncc",
            "best_pass",
            "status",
        ])

        for pass_number in range(1, MAX_PASSES + 1):
            warped = np.asarray(
                nib.load(current_file).dataobj,
                dtype=np.float32,
            )

            if warped.shape != template.shape:
                if warped.shape[::-1] == template.shape:
                    warped = np.transpose(warped, (2, 1, 0))
                else:
                    raise ValueError(
                        f"Shape mismatch: {warped.shape} "
                        f"vs {template.shape}"
                    )

            wncc = compute_wncc_fast(
                template,
                warped,
                mask,
            )

            gain = (
                float("nan")
                if previous_score is None
                else wncc - previous_score
            )

            # Preserve the best result seen, not just the last result.
            if wncc > best_score:
                best_score = wncc
                best_file = current_file
                best_pass = pass_number

            status = "continue"

            if previous_score is not None:
                if gain < 0:
                    # Do not propagate a regressed image into another pass.
                    status = "regression_stop"
                    stop_reason = "score_regressed"
                elif gain < MIN_GAIN:
                    stale_passes += 1

                    if stale_passes >= PATIENCE:
                        status = "plateau_stop"
                        stop_reason = "insufficient_improvement"
                else:
                    stale_passes = 0

            writer.writerow([
                pass_number,
                f"{wncc:.7f}",
                "" if previous_score is None else f"{gain:.7f}",
                f"{best_score:.7f}",
                best_pass,
                status,
            ])
            f.flush()

            print(
                f"Pass {pass_number}: "
                f"WNCC={wncc:.5f}, "
                f"gain={gain:.5f}, "
                f"best={best_score:.5f} "
                f"(pass {best_pass}), "
                f"status={status}"
            )

            if status in ("regression_stop", "plateau_stop"):
                break

            previous_score = wncc

            if pass_number < MAX_PASSES:
                current_file = RegisterPass(
                    current_file,
                    template_name,
                    mask_name,
                    pass_number + 1,
                )

        else:
            stop_reason = "maximum_passes_reached"

    print(
        f"Stopping: {stop_reason}. "
        f"Best pass={best_pass}, "
        f"best WNCC={best_score:.5f}"
    )

    return {
        "best_file": best_file,
        "best_score": best_score,
        "best_pass": best_pass,
        "stop_reason": stop_reason,
    }


# -------------------------------------------------------------------------
# Main
# -------------------------------------------------------------------------

def main():

    folder = os.path.normpath(sys.argv[1])

    if folder.endswith("3Dreg"):
        folder = os.path.dirname(folder)

    reg_dir = os.path.join(folder, "3Dreg")

    img_seq_list = glob.glob(
        os.path.join(reg_dir, "*.tif")
    )

    img_seq_list = [
        f for f in img_seq_list
        if "_warp" not in os.path.basename(f).lower()
        and "template" not in os.path.basename(f).lower()
    ]

    if not img_seq_list:
        raise RuntimeError("No input TIFF files found")

    template_name = os.path.join(
        reg_dir,
        "Newtemplate.tif"
    )

    if not os.path.exists(template_name):

        template_file = FindTemplate(folder)

        tifffile.imwrite(
            template_name,
            tifffile.imread(template_file).astype(np.uint16)
        )

    mask_name='/faststorage/project/FUNCT_ENS/TemplateFiles/Done/'+os.path.basename(folder).split('_range')[0]+'_template.tif'
    if not os.path.exists(mask_name):
     file_name=os.path.basename(img_seq_list[0])
     mask_name=file_name.split('_range')[0]+'_TEMPLATE.tif'
     date_name=mask_name.split('_RS_')[0]
     date_name='20'+date_name[-2:]+date_name[2:4]+date_name[0:2]
     mask_name=os.path.join(os.path.join(folder),'RS_'+date_name+'_'+mask_name.split('_RS_')[1])
    template = tifffile.imread(template_name)
    
    mask = tifffile.imread(mask_name)

    failed = []

    for img_name in img_seq_list:

        try:

            warp1 = Register_single_image(
                img_name,
                template_name,
                mask_name
            )

            result = AdaptiveRegistration(
                first_warp_file=warp1,
                template=template,
                mask=mask,
                template_name=template_name,
                mask_name=mask_name,
                csv_file=img_name + "_metrics.csv"
            )

            best_file = result["best_file"]

            best_tif = img_name + "_Best.tif"

            if not os.path.exists(best_tif):

                img = np.asarray(
                    nib.load(best_file).dataobj,
                    dtype=np.float32
                )

                if img.shape[::-1] == template.shape:
                    img = np.transpose(img, (2,1,0))

                img = np.clip(
                    img,
                    0,
                    65535
                ).astype(np.uint16)

                tifffile.imwrite(
                    best_tif,
                    img,
                    bigtiff=True
                )

        except Exception as e:

            print(f"FAILED: {img_name}")
            print(e)

            failed.append(img_name)

    if failed:

        print(
            f"{len(failed)} file(s) failed"
        )

        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()