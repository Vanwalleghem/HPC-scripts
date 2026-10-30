# -*- coding: utf-8 -*-
"""
Created on Thu Oct 29 08:27:19 2026

@author: au691573
"""

import tifffile
import os
import glob
import cv2
from pathlib import Path
import numpy as np
import pandas as pd

def variance_of_laplacian(gray):
    """Classic blur metric."""
    return cv2.Laplacian(gray, cv2.CV_64F).var()
def brenner(gray):
    """Brenner focus measure."""
    diff = gray[:, 2:].astype(np.float64) - gray[:, :-2].astype(np.float64)
    return np.mean(diff**2)
def analyze_image(gray,image_path):
    if gray is None:
        raise ValueError(f"Could not load image: {image_path}")
    return {
        "filename": image_path.name,
        "width": gray.shape[1],
        "height": gray.shape[0],
        "laplacian_var": variance_of_laplacian(gray),
        "brenner": brenner(gray)
    }

results = []

tif_file_folder='/faststorage/project/FUNCT_ENS/MaxTime'
img_list=sorted(glob.glob(os.path.join(tif_file_folder,'*MaxZ.tif')))
for img in img_list:
    try:
        img_data=tifffile.imread(img)
        idx_time=np.argmax(img_data.shape)
        img_max=img_data.max(axis=idx_time)
        tifffile.imwrite(img.replace('MaxZ','MaxMax'),img_max)
        metrics = analyze_image(img_max,Path(img))
        results.append(metrics)
        print(f"Processed: {img}")
    except Exception as e:
        print(f"Failed: {img} -> {e}")
        continue
    

df = pd.DataFrame(results)
metrics = ["laplacian_var", "brenner"]
for m in metrics:
    df[m + "_norm"] = (
        100 * (df[m] - df[m].min()) /
        (df[m].max() - df[m].min()))
df["sharpness_score"] = df[[m + "_norm" for m in metrics]].mean(axis=1)
df.to_csv("blur_metrics.csv", index=False)


results = []
for img in img_list:
    try:
        img_data=tifffile.imread(img)
        idx_time=np.argmax(img_data.shape)
        img_max=img_data.mean(axis=idx_time)
        tifffile.imwrite(img.replace('MaxZ','MeanMax'),img_max)
        metrics = analyze_image(img_max,Path(img))
        results.append(metrics)
        print(f"Processed: {img}")
    except Exception as e:
        print(f"Failed: {img} -> {e}")
        continue
    

df = pd.DataFrame(results)
metrics = ["laplacian_var", "brenner"]
for m in metrics:
    df[m + "_norm"] = (
        100 * (df[m] - df[m].min()) /
        (df[m].max() - df[m].min()))
df["sharpness_score"] = df[[m + "_norm" for m in metrics]].mean(axis=1)
df.to_csv("blur_metrics_mean.csv", index=False)

df.sort_values("sharpness_score", ascending=False)

