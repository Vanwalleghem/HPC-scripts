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
#os.chdir(os.path.dirname(tif_file_folder))
img_seq_list=glob.glob(os.path.join(tif_file_folder,'3Dreg/','*_Greedy.nii.gz'))
template_file=tif_file_folder+'/3Dreg/template.tif'

for img_name in img_seq_list:
  if not os.path.exists(img_name.replace('Greedy.nii.gz','CombinedWarp.nii.gz')):
    output_name=img_name.replace('Greedy.nii.gz','CombinedWarp.nii.gz')    
    #Combine warps into one warp
    job_string = "antsApplyTransforms -d 3 -o ["+output_name+",1] -t "+img_name.replace('_Greedy.nii.gz','.tif_Greedy2.nii.gz')+" -t "+img_name+" -r "+template_file
    call([job_string],shell=True)  
    #if not os.path.exists(img_name.replace('Greedy.nii.gz','CombinedWarp.nii.gz')): #if it fails, it usually is because of Greedy.nii.gz, so we recompute it
    #    template_name=tif_file_folder+'/3Dreg/template.tif'
    #    Mask_name='/faststorage/project/FUNCT_ENS/TemplateFiles/Done/'+os.path.basename(tif_file_folder).split('_range')[0]+'_template.tif'
    #    Mov_name=img_name.replace('Greedy.nii.gz','.tif')        
    #    Affine_name = Mov_name.replace('.tif','_Greedy_affine.mat')
    #    job_string = "greedy -d 3 -a -float -o Affine_name -i FixImg MovImg -gm MaskImg -n 100x40x20 -e 0.25 -ia-image-centers -m NCC 2x2x2"
    #    job_string = job_string.replace('Affine_name',Affine_name).replace('OutImg',img_name).replace('FixImg',template_name).replace('MovImg',Mov_name).replace('MaskImg',Mask_name)
    #    call([job_string],shell=True)          
    #    job_string = "greedy -d 3 -float -o OutImg.nii -i FixImg MovImg -gm MaskImg -it Affine_name -n 100x50x20 -e 0.25 -m NCC 2x2x2"
    #    job_string = job_string.replace('Affine_name',Affine_name).replace('OutImg',img_name).replace('FixImg',template_name).replace('MovImg',Mov_name).replace('MaskImg',Mask_name)
    #    call([job_string],shell=True)          
    Jacob_name = img_name.split('_Greedy.nii.gz')[0]+'_Jacobian2.nii.gz'
    #Compute the jacobian determinant of all the warps
    job_string = "CreateJacobianDeterminantImage 3 "+output_name+" "+Jacob_name+" 1 0"    
    call([job_string],shell=True)

file_name=os.path.basename(os.path.normpath(tif_file_folder))
if not os.path.exists(tif_file_folder+'/'+file_name+'_3DJacob2.tif'):
  base_img=nib.load(img_seq_list[0])
  base_img=np.squeeze(np.asarray(base_img.get_fdata(),dtype='float32')).transpose()
  range2=int(file_name.split('range')[-1].split('_')[0])
  step=int(file_name.split('step')[-1].split('_')[0])
  TrueSlices=int((range2/step)+1);
  C2frames=np.zeros((int(len(img_seq_list)),base_img.shape[1],base_img.shape[2],base_img.shape[3]))
  for name in img_seq_list:       
      output_name = name.split('_Greedy.nii.gz')[0]+'_Jacobian2.nii.gz'
      img_nb=int( re.search('_(\\d+)_Greedy.nii.gz',name).group(1)) 
      img_temp=nib.load(output_name)
      img_temp=img_temp.get_fdata()    
      img_temp=np.squeeze(np.asarray(img_temp)).transpose()
      C2frames[img_nb,:,:,:]=img_temp
  
  tifffile.imsave(tif_file_folder+'/'+file_name+'_3DJacob2.tif',C2frames)