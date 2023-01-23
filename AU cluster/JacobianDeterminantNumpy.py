from subprocess import call
import time
import glob
import os
import sys
import tifffile
import numpy as np
import nibabel as nib
import gc
import re
from caiman.source_extraction import cnmf
from scipy.io import savemat

tif_file_folder=sys.argv[1]
tif_file_folder=os.path.normpath(tif_file_folder)
print(tif_file_folder)
os.chdir(os.path.dirname(tif_file_folder))
img_seq_list=glob.glob(tif_file_folder+'/3Dreg/*_Greedy.nii')
FourD_File = glob.glob(os.path.join(tif_file_folder,'*_3DJacob2.tif'))

#Only load the metadata to get the dimensions of the image
tif_info=tifffile.TiffFile(FourD_File[0])
dims=tif_info.series[0].shape


base_img=nib.load(img_seq_list[0])
base_img=np.squeeze(np.asarray(base_img.get_fdata(),dtype='float32')).transpose()
file_name=os.path.basename(os.path.normpath(tif_file_folder))
range2=int(file_name.split('range')[-1].split('_')[0])
step=int(file_name.split('step')[-1].split('_')[0])
TrueSlices=int((range2/step)+1);
C2frames=np.zeros((int(len(img_seq_list)),base_img.shape[1],base_img.shape[2],base_img.shape[3]))
for name in img_seq_list:       
    output_name = name.split('_Greedy.nii')[0]+'_Jacobian2.nii'
    img_nb=int( re.search('_(\d+)_Greedy.nii',name).group(1)) 
    img_temp=nib.load(output_name)
    img_temp=img_temp.get_fdata()    
    img_temp=np.squeeze(np.asarray(img_temp)).transpose()
    C2frames[img_nb,:,:,:]=img_temp

matlab_arrays={}
for slice_nb in range(0,base_img.shape[1]):
  SlicedImg=np.squeeze(C2frames[:,slice_nb,:,:]).transpose()
  caiman_filename=os.path.basename(FourD_TifFile[0]).replace('.tif','_slice'+str(slice_nb+1)+'.tif').replace('.tif','b.hdf5')
  caiman_filename=os.path.abspath(os.path.join(tif_file_folder,'../../CaImAn2/',caiman_filename))
  cnm_seed=cnmf.cnmf.load_CNMF(caiman_filename)    
  Ain=cnm_seed.estimates.A.toarray()
  Ain=np.reshape(Ain,(dims[3],dims[2],Ain.shape[1]))
  Time_serie=np.zeros((Ain.shape[2],dims[0]))
  for ROI_nb in range(0,Ain.shape[2]):      
    temp=SlicedImg[:,np.transpose(Ain[:,:,ROI_nb]>0)]      
    Time_serie[ROI_nb,:]=temp.mean(axis=1)

  np.save(caiman_filename.replace('b.hdf5','.npy'),Time_serie)    
  matlab_arrays[str(slice_nb)]=Time_serie

nib_img=nib.Nifti1Image(C2frames.transpose(),np.eye(4))
nib.save(C2frames,tif_file_folder+'/'+file_name+'_3DJacob.nii')
savemat(FourD_File[0].replace('_3DJacob2.tif','.mat'),matlab_arrays)
