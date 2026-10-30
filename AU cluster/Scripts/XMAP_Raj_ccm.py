# -*- coding: utf-8 -*-
"""
Created on Mon Sep  7 12:08:10 2026

@author: au691573
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Jun 23 08:47:36 2026

@author: au691573
"""
import sys
import os, natsort

import glob
#import logging
import numpy as np
from pathlib import Path
os.environ["CAIMAN_TEMP"]="/faststorage/project/FUNCT_ENS/CaImAnTemp/"
import kedm
from caiman.source_extraction import cnmf
from joblib import Parallel, delayed
#import datetime
#from pathlib import Path
opencv=True

def compute_ccm(idx_x, idx_y, timeseries, Embed_dims, tau_value):
    E = np.max([Embed_dims[idx_x], Embed_dims[idx_y]])
    return idx_x, idx_y, kedm.ccm(
        timeseries[:, idx_x],
        timeseries[:, idx_y],
        lib_sizes=[1200],
        sample=5,
        E=E,
        tau=tau_value
    )[0]


#Caiman_file='GV_20200727_fish1_ENS_3DPF_range100_step5_exposure20_power60_MaxZ_Fluor.npy'
Caiman_file=sys.argv[1]
Caiman_file=Caiman_file.split('\r')[0]# removes the return to line
Caiman_file = r"{}".format(Caiman_file)
print(Caiman_file)
tif_file_folder='/faststorage/project/FUNCT_ENS/data/'
tau=10
result_dir='/faststorage/project/FUNCT_ENS/data/XMap_tau'+str(tau)
Path(result_dir).mkdir(parents=True, exist_ok=True)

caiman_filename=glob.glob(os.path.join(tif_file_folder,'**/',Caiman_file),recursive=True)[0]
tif_file_name=os.path.basename(caiman_filename).split('.npy')[0].split('.hdf5')[0]
if not os.path.exists(os.path.join(result_dir,tif_file_name+'_xmap.npy')):
    if caiman_filename.endswith(".hdf5"):
        cnm_seed=cnmf.cnmf.load_CNMF(caiman_filename)
        idx_good=cnm_seed.estimates.idx_components
        timeseries=cnm_seed.estimates.C
        timeseries=timeseries[idx_good,:]
    elif caiman_filename.endswith("Fluor.npy"):
        timeseries=np.load(caiman_filename)
    elif caiman_filename.endswith("timeseries.npy"):
        tif_file_folder=os.path.dirname(caiman_filename)
        Slice_files=glob.glob(os.path.join(tif_file_folder,'*Slice*b.hdf5'))
        Slice_files=natsort.natsorted(Slice_files)
        for caiman_filename in Slice_files:
            slice_nb=int(Slice_files[0].split('_Slice')[1].split('b.hdf5')[0])
            cnm_seed=cnmf.cnmf.load_CNMF(caiman_filename)
            Slice_timeseries=cnm_seed.estimates.C
            Slice_timeseries=Slice_timeseries.transpose()
            if not 'timeseries' in locals():
                timeseries=Slice_timeseries
            else:
                timeseries=np.concatenate((timeseries,Slice_timeseries),axis=1)
            if not timeseries.shape[0]==1200:
              timeseries=timeseries.transpose()
    else:
        print('unrecognized format in caiman filename')
    
    if not timeseries.shape[0]==1200:
      timeseries=timeseries.transpose()
    #ccm_rho=np.full([1], np.nan)
    #count=0
    tau_value=2
    Embed_dims=[None] * timeseries.shape[1]
    for i in range(0,timeseries.shape[1]):
         Embed_dims[i]=kedm.edim(timeseries[:,i],20,tau,1)
    np.save(os.path.join(result_dir,tif_file_name+'_Embed_dims.npy'),Embed_dims)
    ccm_rho=kedm.xmap(timeseries,Embed_dims,tau,1)
    if np.sum(np.isnan(ccm_rho))<100:
        np.save(os.path.join(result_dir,tif_file_name+'_xmap.npy'),ccm_rho)
    else:
        n = timeseries.shape[1]
        chunk_size=100
        for start in range(0, n, chunk_size):
            stop = min(start + chunk_size, n)
            results = Parallel(n_jobs=-1)(
            delayed(compute_ccm)(idx_x, idx_y, timeseries, Embed_dims, tau_value)
            for idx_x in range(start,stop)
             for idx_y in range(n)
             )
            ccm_rho = np.zeros((n, n))
            for idx_x, idx_y, val in results:
               ccm_rho[idx_x, idx_y] = val
            np.save(os.path.join(result_dir,tif_file_name+'_xmap_chunk'+start+'.npy'),ccm_rho)

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



