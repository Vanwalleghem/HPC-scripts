import sys
import os
import shutil
import glob
import os
import tifffile
import numpy as np
import caiman as cm
from caiman.source_extraction import cnmf
import tifffile
from subprocess import call
from scipy.io import savemat


tif_folder=os.path.normpath(sys.argv[1])
FourD_File = glob.glob(os.path.join(tif_folder,'*_3DJacob2.tif'))
caiman_filename = glob.glob(os.path.join(tif_folder,'*4D2b_new2.hdf5'))
print(FourD_File)

cnm_seed=cnmf.cnmf.load_CNMF(caiman_filename[0])
dims=cnm_seed.dims
com=cm.base.rois.com(cnm_seed.estimates.A,*dims)
Ain=cnm_seed.estimates.A
#dims=(*dims,Ain.shape[1])
#Ain=np.reshape(Ain,dims,order='F')

FourD_MemMap=tifffile.memmap(FourD_File[0])
Time_serie=np.zeros((Ain.shape[-1],FourD_MemMap.shape[0]))
for component in range(0,Ain.shape[1]):
    temp_shape=Ain[:,component].toarray()
    #temp_shape=Ain[:,:,:,component]
    temp_shape=temp_shape.reshape(dims,order='F')
    temp_shape=temp_shape.transpose(2,1,0)
    for frame_nb in range(0,FourD_MemMap.shape[0]):
        Time_serie[component,frame_nb]=np.mean(temp_shape*FourD_MemMap[frame_nb])

np.save(caiman_filename[0].replace('b.hdf5','.npy'),Time_serie)
savemat(caiman_filename[0].replace('b.hdf5','.mat'),{'Jacobian':Time_serie})
#savemat(FourD_File[0].replace('_3DJacob2.tif','.mat'),matlab_arrays)