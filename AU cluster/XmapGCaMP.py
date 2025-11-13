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

result_dir='/faststorage/project/FUNCT_ENS/data/XMap2'
Path(result_dir).mkdir(parents=True, exist_ok=True)
hdf5_file=sys.argv[1]
hdf5_file=hdf5_file.split('\r')[0].replace("'","")# removes the return to line  
tif_file_folder='/faststorage/project/FUNCT_ENS/data'
#raw_string = r"{}".format(tif_file_folder)
temp=glob.glob(os.path.join(tif_file_folder,'*/*/',hdf5_file))
tif_file_folder=os.path.normpath(temp[0])
tif_file_name=os.path.basename(temp[0]).split('_4D')[0]

caiman_filename=temp[0]
print('Analyzing '+caiman_filename)
#list_caiman_files=glob.glob(os.path.join(tif_file_folder,'*.hdf5'))
#for caiman_filename in list_caiman_files:
    #caiman_filename = max(list_caiman_files, key=os.path.getctime)
    #if 'Tifflist' in caiman_filename or 'optCaImAn' in caiman_filename:
cnm_seed=cnmf.cnmf.load_CNMF(caiman_filename)
timeseries=cnm_seed.estimates.C
timeseries=timeseries.transpose()
Embed_dims=[None] * timeseries.shape[1]
for i in range(0,timeseries.shape[1]):
    Embed_dims[i]=kedm.edim(timeseries[:,i],10,1,0)
    np.save(os.path.join(result_dir,tif_file_name+'_Embed_dims.npy'),Embed_dims)        
ccm_rho=kedm.xmap(timeseries,Embed_dims,1,0)
np.save(os.path.join(result_dir,tif_file_name+'_xmap.npy'),ccm_rho)
print(tif_file_name)          
                   