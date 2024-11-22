import glob
import os
import sys
import tifffile
import numpy as np
import nibabel as nib
import re


FourD_Files = glob.glob('/faststorage/project/FUNCT_ENS/NewENSDataAU/**/*_4D2.tif', recursive=True)
#FourD_Files = glob.glob('/faststorage/project/FUNCT_ENS/NewENSDataAU/20231217/171223_RS_5DPF_GF_F1_HINDGUT_range135_step5_exposure10_power60/*_4D2.tif')

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
 print(file_name)
 if not glob.glob(FourD_File.replace('4D2','_4D_cropped')):
  mask_name=file_name.split('_range')[0]+'_TEMPLATE.tif'
  date_name=mask_name.split('_RS_')[0]
  date_name='20'+date_name[-2:]+date_name[2:4]+date_name[0:2]
  mask_name=os.path.join(os.path.dirname(FourD_File),'RS_'+date_name+'_'+mask_name.split('_RS_')[1])
  mask_check=tifffile.imread(mask_name)
  crop_dims=bbox2_3D(mask_check)
  dir_name=os.path.dirname(FourD_File)
  MC_img_list=glob.glob(dir_name+'/3Dreg/*_Warped2.nii*') #Will need to be changed to nii.gz eventually
  if not MC_img_list:
   print('Missing warped files')
   continue
  C1_name=MC_img_list[0] 
  range2=int(file_name.split('range')[-1].split('_')[0])
  step=int(file_name.split('step')[-1].split('_')[0])
  TrueSlices=int((range2/step)+1);    
  base_img=nib.load(C1_name)
  Y=np.squeeze(np.asarray(base_img.get_fdata(dtype='float16'),dtype='uint16')).transpose()
  Y=Y[:,max(crop_dims[2]-10,0):min(crop_dims[3]+10,Y.shape[1]),max(crop_dims[4]-10,0):min(crop_dims[5]+10,Y.shape[1])]  
  C1frames=np.zeros((int(len(MC_img_list)),TrueSlices,Y.shape[1],Y.shape[2]), dtype='uint16')
  for img_nb,C2_name in enumerate(MC_img_list):    
   img_nb=int( re.search('_power.+_time(\d+)\.tif',C2_name).group(1)) 
   try:
    img_temp=nib.load(C2_name)
    img_temp=img_temp.slicer[max(crop_dims[4]-10,0):min(crop_dims[5]+10,mask_check.shape[1]),max(crop_dims[2]-10,0):min(crop_dims[3]+10,mask_check.shape[1]),:].get_fdata(dtype='float16')
   except:
    break       
   Y=img_temp
   Y=np.squeeze(np.asarray(Y,dtype='uint16')).transpose()
   C1frames[img_nb,:,:,:]=Y
  tifffile.imwrite(FourD_File.replace('4D2','_4D_cropped'),C1frames)
  print(os.path.dirname(FourD_File) + 'is done')
  
 else:
  print(os.path.dirname(FourD_File) + 'was already done')