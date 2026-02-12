import glob
import os
import tifffile
import numpy as np

def bbox2_3D(img):
    r = np.any(img, axis=(1, 2))
    c = np.any(img, axis=(0, 2))
    z = np.any(img, axis=(0, 1))
    rmin, rmax = np.where(r)[0][[0, -1]]
    cmin, cmax = np.where(c)[0][[0, -1]]
    zmin, zmax = np.where(z)[0][[0, -1]]
    return rmin, rmax, cmin, cmax, zmin, zmax

folder='/faststorage/project/FUNCT_ENS/NewENSDataDK/'
base_folder=folder
fnames_all =[]

for file1 in glob.glob(os.path.join(base_folder,'**/3Dreg/'),recursive=True):
 file1=os.path.normpath(file1.split('/3Dreg')[0])
 fnames_all.append(file1)

for folder in fnames_all:
 files_name=glob.glob(os.path.join(folder,'3Dreg/','*Warped3.tif'))
 file_name=os.path.basename(folder)
 cropped_files=glob.glob(os.path.join(folder,'3Dreg/','*Warped3crop.tif'))
 if not files_name:
  continue
 if len(cropped_files)<1200:
  file_name=os.path.basename(folder)
  mask_name=file_name.split('_range')[0]+'_TEMPLATE.tif'
  date_name=mask_name.split('_RS_')[0]
  date_name='20'+date_name[-2:]+date_name[2:4]+date_name[0:2]
  mask_name=os.path.join(folder,'RS_'+date_name+'_'+mask_name.split('_RS_')[1])
  mask_check=tifffile.imread(mask_name)
  crop_dims=bbox2_3D(mask_check)
  try:
   for FourD_File in files_name:
    if not os.path.exists(FourD_File.replace('Warped3.tif','Warped3crop.tif')):
     Y=tifffile.imread(FourD_File)
     Y=Y[max(crop_dims[4]-10,0):min(crop_dims[5]+10,Y.shape[1]),max(crop_dims[2]-10,0):min(crop_dims[3]+10,Y.shape[1]),:]
     tifffile.imwrite(FourD_File.replace('Warped3.tif','Warped3crop.tif'),Y.astype(np.uint16))
  except:
   print(FourD_File)