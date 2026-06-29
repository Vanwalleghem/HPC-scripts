# -*- coding: utf-8 -*-
"""
Created on Mon Aug 11 15:47:00 2025

@author: au691573
"""

import numpy as np
from caiman.source_extraction import cnmf
import os
import glob
import kedm
import sys
from pathlib import Path
import nibabel as nib
import natsort
import re

result_dir='/faststorage/project/FUNCT_ENS/data/XMapJacob2'
Path(result_dir).mkdir(parents=True, exist_ok=True)
tif_file_folder='/faststorage/project/FUNCT_ENS/data/20200729/GV_20200729_fish1_ENSGF_5DPF_range140_step5_exposure17_power60/'
tif_file_folder=sys.argv[1]
tif_file_folder=os.path.normpath(tif_file_folder)
print(tif_file_folder)
if glob.glob(os.path.join(tif_file_folder,'3Dreg/*_Jacobian3.nii.gz')):
 img_seq_list=glob.glob(os.path.join(tif_file_folder,'3Dreg/*_Jacobian3.nii.gz'))
 Jacob_nb=3
else:
 img_seq_list=glob.glob(os.path.join(tif_file_folder,'3Dreg/*_Jacobian2.nii.gz'))
 Jacob_nb=2

base_img=nib.load(img_seq_list[0])
dims=base_img.header.get_data_shape()
T=len(img_seq_list)

Jacob_img=np.zeros(((T,)+dims),dtype=np.float16)
for name in img_seq_list:
  img_nb=int( re.search(r'_(\d+)_Jacobian',name).group(1)) 
  img_temp=nib.load(name)
  img_temp=img_temp.get_fdata(dtype=np.float16)
  Jacob_img[img_nb,:]=img_temp

Slice_files=glob.glob(os.path.join(tif_file_folder,'*NewSlice*Temp.hdf5'))
Slice_files=natsort.natsorted(Slice_files)
if 'timeseries' in locals():
 del timeseries

caiman_filename=Slice_files[0]
for caiman_filename in Slice_files:
 #caiman_filename = max(list_caiman_files, key=os.path.getctime)
    slice_nb=int(Slice_files[0].split('_Slice')[1].split('_')[0])
    cnm_seed=cnmf.cnmf.load_CNMF(caiman_filename)
    Ain=cnm_seed.estimates.A.toarray()
    Ain=np.reshape(Ain,(cnm_seed.dims[0],cnm_seed.dims[1],Ain.shape[1]))
    Time_serie=np.zeros((Ain.shape[-1],T))
    for ROI_nb in range(0,Ain.shape[-1]):
         temp=Jacob_img[:,Ain[:,:,ROI_nb]>0,slice_nb]
         weights=Ain[Ain[:,:,ROI_nb]>0,ROI_nb]
         avg_Jacob=np.average(temp, weights=weights,axis=1)
         Time_serie[ROI_nb,:]=avg_Jacob
    if not 'timeseries' in locals():
        timeseries=Time_serie            
    else:
        timeseries=np.concatenate((timeseries,Time_serie),axis=1)
    np.save(os.path.join(tif_file_folder,os.path.basename(tif_file_folder).split('_range')[0]+'_JacobianSlice'+str(slice_nb)+'.npy'),Time_serie)

np.save(os.path.join(tif_file_folder,os.path.basename(tif_file_folder).split('_range')[0]+'_JacobianSlices.npy'),timeseries)

Jacob_timeseries=timeseries
Jacob_timeseries=Jacob_timeseries.transpose()

if os.path.join(tif_file_folder,os.path.basename(tif_file_folder)+'_timeseries.npy'):
  timeseries=np.load(os.path.join(tif_file_folder,os.path.basename(tif_file_folder)+'_timeseries.npy'))
else:
    print('need to concatenate Slices')
    exit()

timeseries=np.concatenate((timeseries,Jacob_timeseries),axis=1)
tif_file_name=os.path.basename(tif_file_folder)
caiman_regex='Slices'

Embed_dims=[None] * timeseries.shape[1]
for i in range(0,timeseries.shape[1]):
    Embed_dims[i]=kedm.edim(timeseries[:,i],20,5,1)
    np.save(os.path.join(result_dir,tif_file_name+'_JacGCaMP'+caiman_regex+'_Embed_dims.npy'),Embed_dims)

ccm_rho=kedm.xmap(timeseries,Embed_dims,5,1)
np.save(os.path.join(result_dir,tif_file_name+'_JacGCaMP'+caiman_regex+'_xmap.npy'),ccm_rho)
