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

result_dir='/faststorage/project/FUNCT_ENS/data/XMapJacob'
Path(result_dir).mkdir(parents=True, exist_ok=True)
Jacob_file=sys.argv[1]
Jacob_file=Jacob_file.split('\r')[0].replace("'","")# removes the return to line  
tif_file_name=os.path.basename(Jacob_file).split('_Jacobian')[0]
caiman_regex=os.path.basename(Jacob_file).split('_Jacobian')[1].split('.npy')[0]
list_caiman_files=glob.glob(os.path.join(os.path.dirname(Jacob_file),'*'+caiman_regex+'.hdf5'))
if len(list_caiman_files)>1:
    print('ambiguous caiman file :'+tif_file_name)
    exit()
elif len(list_caiman_files)==0:
    print('missing caiman file :'+tif_file_name)
    exit()
    

caiman_filename=list_caiman_files[0]
cnm_seed=cnmf.cnmf.load_CNMF(caiman_filename)
timeseries=cnm_seed.estimates.C
timeseries=timeseries.transpose()

Jacob_timeseries=np.load(Jacob_file)
Jacob_timeseries=Jacob_timeseries.transpose()

timeseries=np.concatenate((timeseries,Jacob_timeseries),axis=1)

Embed_dims=[None] * timeseries.shape[1]
for i in range(0,timeseries.shape[1]):
    Embed_dims[i]=kedm.edim(timeseries[:,i],10,1,0)
    np.save(os.path.join(result_dir,tif_file_name+'_JacGCaMP'+caiman_regex+'_Embed_dims.npy'),Embed_dims)        
ccm_rho=kedm.xmap(timeseries,Embed_dims,1,0)
np.save(os.path.join(result_dir,tif_file_name+'_JacGCaMP'+caiman_regex+'_xmap.npy'),ccm_rho)
