import sys
import os

import glob
#import logging
import numpy as np
import natsort
from pathlib import Path
import kedm

tif_file_folder=sys.argv[1]
tif_file_folder=tif_file_folder.split('\r')[0]# removes the return to line

result_dir='/faststorage/project/FUNCT_ENS/data/XMap4'
Path(result_dir).mkdir(parents=True, exist_ok=True)

Slice_files=glob.glob(os.path.join(tif_file_folder,'*uor.npy'))
Slice_files=natsort.natsorted(Slice_files)
if 'timeseries' in locals():
 del timeseries

for stardist_filename in Slice_files:
    timeseries=np.load(stardist_filename)
    tif_file_name=os.path.basename(stardist_filename).split('MaxZ')[0]
    Embed_dims=[None] * timeseries.shape[1]
    for i in range(0,timeseries.shape[1]):
        Embed_dims[i]=kedm.edim(timeseries[:,i],20,2,1)
    np.save(os.path.join(result_dir,tif_file_name+'_Embed_dimsSlices.npy'),Embed_dims)
    ccm_rho=kedm.xmap(timeseries,Embed_dims,2,1)
    np.save(os.path.join(result_dir,tif_file_name+'_xmapSlices.npy'),ccm_rho)