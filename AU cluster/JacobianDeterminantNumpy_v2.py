# -*- coding: utf-8 -*-
"""
Created on Mon Jan 23 14:07:34 2023

@author: au691573
"""

import glob
import os
import sys
import numpy as np
import nibabel as nib
import re
from caiman.source_extraction import cnmf
from scipy.io import savemat

tif_file_folder=sys.argv[1]
tif_file_folder=os.path.normpath(tif_file_folder)
print(tif_file_folder)
if glob.glob(os.path.join(tif_file_folder,'3Dreg/','*_Jacobian3.nii.gz')):
 img_seq_list=glob.glob(os.path.join(tif_file_folder,'3Dreg/','*_Jacobian3.nii.gz'))
 Jacob_nb=3
else:
 img_seq_list=glob.glob(os.path.join(tif_file_folder,'3Dreg/','*_Jacobian2.nii.gz'))
 Jacob_nb=2

#Only load the metadata to get the dimensions of the image
base_img=nib.load(img_seq_list[0])
dims=base_img.header.get_data_shape()
T=len(img_seq_list)

#base_img=np.squeeze(np.asarray(base_img.get_fdata(),dtype='float32')).transpose()
#file_name=os.path.basename(os.path.normpath(tif_file_folder))
#C2frames=np.zeros([T]+list(dims))
#for name in img_seq_list:           
#    img_nb=int( re.search('power\d+_(\d+)_Jacobian',name).group(1)) 
#    img_temp=nib.load(name)
#    img_temp=img_temp.get_fdata()
    #img_temp=np.squeeze(np.asarray(img_temp)).transpose()
#    C2frames[img_nb,:,:,:]=img_temp

#matlab_arrays={}  
list_caiman_files=glob.glob(os.path.join(tif_file_folder,'*.hdf5'))
for caiman_filename in list_caiman_files:
 #caiman_filename = max(list_caiman_files, key=os.path.getctime)
 if 'Tifflist' in caiman_filename or 'optCaImAn' in caiman_filename:
  if not os.path.isfile(os.path.join(tif_file_folder,os.path.basename(tif_file_folder).split('_range')[0]+'_Jacobian'+caiman_filename.split('_')[-1].split('.hdf5')[0]+'.npy')):
   cnm_seed=cnmf.cnmf.load_CNMF(caiman_filename)    
   Ain=cnm_seed.estimates.A.toarray()
   Ain=np.reshape(Ain,(cnm_seed.dims[0],cnm_seed.dims[1],cnm_seed.dims[2],Ain.shape[1]))
   Time_serie=np.zeros((Ain.shape[-1],T))
   for name in img_seq_list:
     img_nb=int( re.search('power\d+_(\d+)_Jacobian',name).group(1)) 
     img_temp=nib.load(name)
     img_temp=img_temp.get_fdata()
     for ROI_nb in range(0,Ain.shape[-1]):        
         temp=img_temp[Ain[:,:,:,ROI_nb]>0]
         weights=Ain[Ain[:,:,:,ROI_nb]>0,ROI_nb]
         avg_Jacob=np.average(temp, weights=weights) #use the Ain values to weight the Jacobian
         Time_serie[ROI_nb,img_nb]=avg_Jacob
   np.save(os.path.join(tif_file_folder,os.path.basename(tif_file_folder).split('_range')[0]+'_Jacobian'+caiman_filename.split('_')[-1].split('.hdf5')[0]+'.npy'),Time_serie)
   #savemat(os.path.join(tif_file_folder,os.path.basename(tif_file_folder).split('_range')[0]+'_Jacobian'+caiman_filename.split('_')[-1].split('.hdf5')[0]+'.mat'),Time_serie)
 else:
     continue

