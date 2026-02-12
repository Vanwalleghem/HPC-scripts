# -*- coding: utf-8 -*-
"""
Created on Wed Jan  8 10:06:54 2025

@author: au691573
"""

import numpy as np
import sys
import os
import glob
import tifffile
import nibabel as nib
from subprocess import call

print(sys.argv)
tif_file_folder=sys.argv[1]
tif_file_folder=tif_file_folder.split('\r')[0]# removes the return to line
raw_string = r"{}".format(tif_file_folder)
print(raw_string)
fnames=[os.path.normpath(tif_file_folder)]

#Check if there are some .nii files left
Warped_files=glob.glob(os.path.join(fnames[0],'3Dreg/*Warped*.nii'))
#if Warped_files:
# call('find '+fnames[0]+' -type f -name "*.nii" -exec gzip {} -f \;')

print(fnames)

#file = glob.glob(os.path.join(fnames[0],'*4D2.tif'))
Warped_files=glob.glob(os.path.join(fnames[0],'3Dreg/*Warped3.nii.gz'))
if len(Warped_files)<1200:
 #Warped_files=glob.glob(os.path.join(fnames[0],'3Dreg/*Warped2.nii.gz')) 
 with open('ToCheckConvert.txt', 'a') as f:  
  f.write("%s\n" % fnames[0])
 print('not enough warped3.tif files')
 exit() 
print(Warped_files[0])

if not os.path.isfile(Warped_files[0].replace('.nii.gz','.tif')):
    for file_warped in Warped_files:
        base_img=nib.load(file_warped)
        base_img=np.squeeze(np.asarray(base_img.get_fdata(),dtype='uint16'))
        tifffile.imwrite(file_warped.replace('.nii.gz','.tif'),base_img,bigtiff=True)

print('finished processing') 