from subprocess import call
import time
import glob
import os
import sys
import tifffile
import numpy as np
import nibabel as nib
import multiprocessing as mp
from scipy import signal

tif_file=sys.argv[1]
print(tif_file.replace('.tif',''))
os.chdir(tif_file.replace('.tif',''))
directory = os.getcwd()
new_dir=tif_file.replace('.tif','')

list_img = glob.glob(new_dir+'/*Reg.nii')    
list_img.sort()
name=list_img[0]    
if not os.path.isfile(name.replace('.nii','_3D.tif')):
    base_img=nib.load(name)
    base_img=np.squeeze(np.asarray(base_img.get_fdata(),dtype='float32'))
    frames=np.zeros((len(list_img),base_img.shape[1],base_img.shape[0]), dtype='uint32')
    for img_nb,C1_name in enumerate(list_img):    
        img_temp=nib.load(C1_name)
        img_temp=img_temp.get_fdata()    
        img_temp=np.squeeze(np.asarray(img_temp,dtype='uint32'))
        frames[img_nb,:,:]=np.flipud(np.rot90(img_temp,1))    
    tifffile.imsave(name.replace('.nii','_3D.tif'),frames)
