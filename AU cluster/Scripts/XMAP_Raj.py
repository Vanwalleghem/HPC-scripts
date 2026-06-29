# -*- coding: utf-8 -*-
"""
Created on Tue Jun 23 08:47:36 2026

@author: au691573
"""

import sys
import os

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


Caiman_file=sys.argv[1]

#tif_file_folder='/faststorage/project/FUNCT_ENS/data/20200731/GV_20200731_fish4_ENSFed_7DPF_range140_step5_exposure17_power60'
tif_file_folder='/faststorage/project/FUNCT_ENS/data/'

result_dir='/faststorage/project/FUNCT_ENS/data/XMap4'
Path(result_dir).mkdir(parents=True, exist_ok=True)

caiman_filename=glob.glob(os.path.join(tif_file_folder,'**/',Caiman_file),recursive=True)[0]

cnm_seed=cnmf.cnmf.load_CNMF(caiman_filename)
timeseries=cnm_seed.estimates.C
timeseries=timeseries.transpose()


tif_file_name=Caiman_file.split('_exposure')[0]
Embed_dims=[None] * timeseries.shape[1]
for i in range(0,timeseries.shape[1]):
    Embed_dims[i]=kedm.edim(timeseries[:,i],20,2,1)

np.save(os.path.join(result_dir,tif_file_name+'_Embed_dimsSlices.npy'),Embed_dims)

ccm_rho=kedm.xmap(timeseries,Embed_dims,2,1)
np.save(os.path.join(result_dir,tif_file_name+'_xmapSlices.npy'),ccm_rho)