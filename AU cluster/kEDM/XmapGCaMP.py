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

result_dir='/faststorage/project/FUNCT_ENS/data/XMap'
Path(result_dir).mkdir(parents=True, exist_ok=True)
tif_file_folder=sys.argv[1]
tif_file_folder=os.path.normpath(tif_file_folder)
tif_file_name=os.path.basename(tif_file_folder).split('_range')[0]

list_caiman_files=glob.glob(os.path.join(tif_file_folder,'*.hdf5'))
for caiman_filename in list_caiman_files:
    #caiman_filename = max(list_caiman_files, key=os.path.getctime)
    if 'Tifflist' in caiman_filename or 'optCaImAn' in caiman_filename:
        cnm_seed=cnmf.cnmf.load_CNMF(caiman_filename)
        timeseries=cnm_seed.estimates.C
        timeseries=timeseries.transpose()
        Embed_dims=[None] * timeseries.shape[1]
        for i in range(0,timeseries.shape[1]):
            Embed_dims[i]=kedm.edim(timeseries[:,i],10,1,0)
            np.save(os.path.join(result_dir,tif_file_name+'_Embed_dims.npy'),Embed_dims)        
        ccm_rho=kedm.xmap(timeseries,Embed_dims,1,0)
        np.save(os.path.join(result_dir,tif_file_name+'_xmap.npy'),ccm_rho)              
                           