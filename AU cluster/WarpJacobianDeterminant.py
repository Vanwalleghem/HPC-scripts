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

tif_file_folder=sys.argv[1]
tif_file_folder=os.path.normpath(tif_file_folder)
print(tif_file_folder)
os.chdir(os.path.dirname(tif_file_folder))
img_seq_list=glob.glob(tif_file_folder+'/3Dreg/*_Greedy.nii')

for img_name in img_seq_list:
  job_string = "antsApplyTransforms -d 3 -o ["+output_image+",1] -t "+img_name.replace('Greedy','Greedy2')+" -t "+img_name+" "+output_name+" 1 0"


base_img=nib.load(img_seq_list[0])
base_img=np.squeeze(np.asarray(base_img.get_fdata(),dtype='float32')).transpose()

for img_name in img_seq_list:
    output_name = img_name.split('_Greedy.nii')[0]+'_Jacobian.nii'
    #Compute the jacobian determinant of all the warps
    job_string = "CreateJacobianDeterminantImage 3 "+img_name+" "+output_name+" 1 0"    
    call([job_string],shell=True)


file_name=os.path.basename(os.path.normpath(tif_file_folder))
range2=int(file_name.split('range')[-1].split('_')[0])
step=int(file_name.split('step')[-1].split('_')[0])
TrueSlices=int((range2/step)+1);
C2frames=np.zeros((int(len(img_seq_list)),base_img.shape[1],base_img.shape[2],base_img.shape[3]))
for name in img_seq_list:       
    output_name = name.split('_Greedy.nii')[0]+'_Jacobian.nii'
    img_nb=int( re.search('_power\d+_(\d+)_Greedy.nii',name).group(1)) 
    img_temp=nib.load(output_name)
    img_temp=img_temp.get_fdata()    
    img_temp=np.squeeze(np.asarray(img_temp)).transpose()
    C2frames[img_nb,:,:,:]=img_temp

tifffile.imsave(tif_file_folder+'/'+file_name+'_3DJacob.tif',C2frames)