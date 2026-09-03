# -*- coding: utf-8 -*-
"""
Created on Tue Jun 23 08:47:36 2026

@author: au691573
"""
import sys
import os
import natsort
import glob
#import logging
import numpy as np
from pathlib import Path
os.environ["CAIMAN_TEMP"]="/faststorage/project/FUNCT_ENS/CaImAnTemp/"
import kedm
from caiman.source_extraction import cnmf

#import datetime
#from pathlib import Path
opencv=True

#Caiman_file='GV_20200727_fish8_ENSGF_4DPF_range140_step5_exposure17_power60_4D2_optCaImAn.hdf5'
Caiman_file=sys.argv[1]
Caiman_file=Caiman_file.split('\r')[0]# removes the return to line
Caiman_file = r"{}".format(Caiman_file)
print(Caiman_file)
tif_file_folder='/faststorage/project/FUNCT_ENS/data/'
tau=2
result_dir='/faststorage/project/FUNCT_ENS/data/XMap_tau'+str(tau)
Path(result_dir).mkdir(parents=True, exist_ok=True)

tif_file_folder=glob.glob(os.path.join(tif_file_folder,'**/',Caiman_file),recursive=True)[0]

Slice_files=glob.glob(os.path.join(tif_file_folder,'*Slice*b.hdf5'))
#Slice_files=[x for x in Slice_files if 'Temp' not in x and 'b.' not in x]
Slice_files=natsort.natsorted(Slice_files)
if 'GCaMP_timeseries' in locals():
 del GCaMP_timeseries

tif_file_name=os.path.basename(tif_file_folder).split('.npy')[0].split('.hdf5')[0]
if not os.path.exists(os.path.join(result_dir,tif_file_name+'timeseries_xmap.npy')):
    for caiman_filename in Slice_files:
        slice_nb=int(Slice_files[0].split('_Slice')[1].split('b.hdf5')[0])
        cnm_seed=cnmf.cnmf.load_CNMF(caiman_filename)
        Slice_timeseries=cnm_seed.estimates.C
        Slice_timeseries=Slice_timeseries.transpose()
        if not 'GCaMP_timeseries' in locals():
            GCaMP_timeseries=Slice_timeseries
        else:
            GCaMP_timeseries=np.concatenate((GCaMP_timeseries,Slice_timeseries),axis=1)
        if not GCaMP_timeseries.shape[0]==1200:
          GCaMP_timeseries=GCaMP_timeseries.transpose()
    Embed_dims=[None] * GCaMP_timeseries.shape[1]
    for i in range(0,GCaMP_timeseries.shape[1]):
         Embed_dims[i]=kedm.edim(GCaMP_timeseries[:,i],20,tau,1)
    np.save(os.path.join(result_dir,tif_file_name+'_Embed_dims.npy'),Embed_dims) 
    ccm_rho=kedm.xmap(GCaMP_timeseries,Embed_dims,tau,1)
    np.save(os.path.join(result_dir,tif_file_name+'_xmap.npy'),ccm_rho)

#cnm_seed=cnmf.cnmf.load_CNMF(caiman_filename)
#timeseries=cnm_seed.estimates.C
#timeseries_filenames=glob.glob(os.path.join(tif_file_folder,'**/*timeseries.npy'),recursive=True)
#for timeseries_filename in timeseries_filenames:
 #timeseries=np.load(timeseries_filename)
 #if not timeseries.shape[0]==1200:
  #timeseries=timeseries.transpose()  
 #tif_file_name=Caiman_file.split('.hdf5')[0]
 #tif_file_name=os.path.basename(timeseries_filename).split('.npy')[0]
 #Embed_dims=[None] * timeseries.shape[1]
 #for i in range(0,timeseries.shape[1]):
 #    Embed_dims[i]=kedm.edim(timeseries[:,i],20,5,1)
 
 #np.save(os.path.join(result_dir,tif_file_name+'_Embed_dimsSlices.npy'),Embed_dims)
 #np.save(os.path.join(result_dir,tif_file_name+'_Embed_dims.npy'),Embed_dims)
 
 #ccm_rho=kedm.xmap(timeseries,Embed_dims,5,1)
# np.save(os.path.join(result_dir,tif_file_name+'_xmapSlices.npy'),ccm_rho)
#np.save(os.path.join(result_dir,tif_file_name+'_xmap.npy'),ccm_rho)



