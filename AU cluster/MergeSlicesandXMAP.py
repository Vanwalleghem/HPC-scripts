import sys
import os

import glob
#import logging
import numpy as np
import natsort
from pathlib import Path
os.environ["CAIMAN_TEMP"]="/faststorage/project/FUNCT_ENS/CaImAnTemp/"
import kedm
import caiman as cm
from caiman.source_extraction import cnmf

#import datetime
#from pathlib import Path
opencv=True


tif_file_folder=sys.argv[1]
#tif_file_folder='/faststorage/project/FUNCT_ENS/data/20200731/GV_20200731_fish4_ENSFed_7DPF_range140_step5_exposure17_power60'
tif_file_folder=tif_file_folder.split('\r')[0]# removes the return to line

result_dir='/faststorage/project/FUNCT_ENS/data/XMap3'
Path(result_dir).mkdir(parents=True, exist_ok=True)

Slice_files=glob.glob(os.path.join(tif_file_folder),'*Slice*.hdf5')
Slice_files=natsort.natsorted(Slice_files)
del timeseries
for caiman_filename in Slice_files:
    cnm_seed=cnmf.cnmf.load_CNMF(caiman_filename)
    Slice_timeseries=cnm_seed.estimates.C
    Slice_timeseries=Slice_timeseries.transpose()
    ROIs=cnm_seed.estimates.A
    Slice_ROI_com=cm.base.rois.com(ROIs,cnm_seed.dims[0],cnm_seed.dims[1])
    Slice_nb=int(caiman_filename.split('_Slice')[1].split('_Temp')[0])
    z_com=np.ones((Slice_ROI_com.shape[0],1))*Slice_nb
    if not 'timeseries' in locals():
        timeseries=Slice_timeseries
        ROI_com=np.concatenate((Slice_ROI_com, z_com),axis=1)
    else:
        timeseries=np.concatenate((timeseries,Slice_timeseries),axis=1)
        temp=np.concatenate((Slice_ROI_com, z_com),axis=1)
        ROI_com=np.concatenate((ROI_com, temp),axis=0)

tif_file_name=os.path.basename(tif_file_folder)
Embed_dims=[None] * timeseries.shape[1]
for i in range(0,timeseries.shape[1]):
    Embed_dims[i]=kedm.edim(timeseries[:,i],10,1,0)
    np.save(os.path.join(result_dir,tif_file_name+'_Embed_dimsSlices.npy'),Embed_dims)

ccm_rho=kedm.xmap(timeseries,Embed_dims,1,0)
np.save(os.path.join(result_dir,tif_file_name+'_xmapSlices.npy'),ccm_rho)


np.save(os.path.join(tif_file_folder,os.path.basename(tif_file_folder)+'_timeseries.npy'),timeseries)
np.save(os.path.join(tif_file_folder,os.path.basename(tif_file_folder)+'_ROIs.npy'),ROI_com)