import time
import glob
import os
import sys
import tifffile
import numpy as np

FourD_Files = glob.glob('/faststorage/project/FUNCT_ENS/NewENSDataAU/**/*_4D2.tif', recursive=True)

def bbox2_3D(img):
    r = np.any(img, axis=(1, 2))
    c = np.any(img, axis=(0, 2))
    z = np.any(img, axis=(0, 1))
    rmin, rmax = np.where(r)[0][[0, -1]]
    cmin, cmax = np.where(c)[0][[0, -1]]
    zmin, zmax = np.where(z)[0][[0, -1]]
    return rmin, rmax, cmin, cmax, zmin, zmax

for FourD_File in FourD_Files:
 file_name=os.path.basename(FourD_File) 
 if not glob.glob(FourD_File.replace('4D2','crop')):
  print(FourD_File)
  mask_name=file_name.split('_range')[0]+'_TEMPLATE.tif'
  date_name=mask_name.split('_RS_')[0]
  date_name='20'+date_name[-2:]+date_name[2:4]+date_name[0:2]
  mask_name=os.path.join(os.path.dirname(FourD_File),'RS_'+date_name+'_'+mask_name.split('_RS_')[1])
  mask_check=tifffile.imread(mask_name)
  crop_dims=bbox2_3D(mask_check)
  Y=tifffile.imread(FourD_File)
  Y=Y[:,max(crop_dims[2]-10,0):min(crop_dims[3]+10,Y.shape[1]),max(crop_dims[4]-10,0):min(crop_dims[5]+10,Y.shape[1])]
  tifffile.imwrite(FourD_File.replace('4D2','crop'),Y.astype(np.uint16))