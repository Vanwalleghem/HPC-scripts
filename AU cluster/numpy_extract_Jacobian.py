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
FourD_TifFile = glob.glob(os.path.join(tif_folder,'*4D2.tif'))
print(FourD_File)
#Y=tifffile.imread(FourD_File[0])
#dims=Y.shape
#Only load the metadata to get the dimensions of the image
tif_info=tifffile.TiffFile(FourD_File[0])
dims=tif_info.series[0].shape

#%% start a cluster for parallel processing (if a cluster already exists it will be closed and a new session will be opened)
matlab_arrays={}
for slice_nb in range(0,dims[1]):
    fnames=[os.path.join(tif_folder,'temp.tif')]
    caiman_filename=os.path.basename(FourD_TifFile[0]).replace('.tif','_slice'+str(slice_nb+1)+'.tif').replace('.tif','b.hdf5')
    caiman_filename=os.path.abspath(os.path.join(tif_folder,'../../CaImAn2/',caiman_filename))
    SlicedImg=tifffile.imread(FourD_File[0],key=range(slice_nb,len(tif_info.pages),dims[1]))    
    cnm_seed=cnmf.cnmf.load_CNMF(caiman_filename)    
    Ain=cnm_seed.estimates.A.toarray()
    Ain=np.reshape(Ain,(dims[3],dims[2],Ain.shape[1]))
    Time_serie=np.zeros((Ain.shape[2],dims[0]))
    for ROI_nb in range(0,Ain.shape[2]):      
      temp=SlicedImg[:,np.transpose(Ain[:,:,ROI_nb]>0)]      
      Time_serie[ROI_nb,:]=temp.mean(axis=1)
      
    np.save(caiman_filename.replace('b.hdf5','.npy'),Time_serie)    
    matlab_arrays[str(slice_nb)]=Time_serie
savemat(FourD_File[0].replace('_3DJacob2.tif','.mat'),matlab_arrays)