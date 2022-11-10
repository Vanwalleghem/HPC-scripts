from subprocess import call
import time
import glob
import os
import sys
import tifffile
from skimage import io
import numpy as np
import nibabel as nib
import multiprocessing as mp
from scipy import signal
import gc
import re
import nrrd

#greedy -d 3 -rf template.tif -rm GV_20200727_fish1_ENSGF_4DPF_range120_step5_exposure20_power60_9.tif_Warped.nii test.nii -r GV_20200727_fish1_ENSGF_4DPF_range120_step5_exposure20_power60_9.tif_Greedy2.nii

def is_file_empty(file_path):
    """ Check if file is empty by confirming if its size is 0 bytes"""
    # Check if file exist and it is empty    
    if os.path.exists(file_path):
        if os.stat(file_path).st_size == 0:
            return True
        else:
            return False
    else:
        return True 

def Register_single_image_noMask_SecondPass(Mov_name,template_name):        
    output_name = Mov_name.replace('_Warped.nii','_Greedy2')    
    if is_file_empty(output_name+'.nii'):
        job_string = "greedy -d 3 -o OutImg.nii -i FixImg MovImg -sv -n 200x100x50 -e 0.25 -m NCC 3x3x3"
        job_string = job_string.replace('OutImg',output_name).replace('FixImg',template_name).replace('MovImg',Mov_name)
        call([job_string],shell=True)          
    output_image = Mov_name.replace('_Warped.nii','_Warped2')
    if is_file_empty(output_image+'.nii'):    
        job_string = "greedy -d 3 -rf FixImg -rm MovImg OutImg.nii -r "+output_name+'.nii'
        job_string = job_string.replace('OutImg',output_image).replace('FixImg',template_name).replace('MovImg',Mov_name)
        call([job_string],shell=True)
    
tif_file_folder=sys.argv[1]
tif_file_folder=os.path.normpath(tif_file_folder)
print(tif_file_folder)
os.chdir(os.path.dirname(tif_file_folder))
img_seq_list=glob.glob(tif_file_folder+'/3Dreg/*_Warped.nii')
template_name=tif_file_folder+'/3Dreg/template.tif'

for MovImg in img_seq_list:
 WarpName=MovImg.replace('_Warped.nii','_Greedy2.nii')
 OutName=MovImg.replace('_Warped.nii','_Warped2.nii')
 if  is_file_empty(OutName):
  job_string = 'greedy -d 3 -rf '+template_name+' -rm '+ MovImg+' '+OutName+' -r '+WarpName
 call([job_string],shell=True)
 print(MovImg)

MC_img_list=glob.glob(tif_file_folder+'/3Dreg/*'+os.path.basename(os.path.normpath(tif_file_folder))+'*_Warped2.nii')    

print(tif_file_folder+' '+str(len(MC_img_list)))    
#f = open(tif_file_folder+'/ListOfFailedFiles.txt','w')
file_name=os.path.basename(os.path.normpath(tif_file_folder))
#if len(MC_img_list)==1200 and not os.path.exists(tif_file_folder+'/'+file_name+'_4D2.tif'):
C1_name=MC_img_list[0] 
range2=int(file_name.split('range')[-1].split('_')[0])
step=int(file_name.split('step')[-1].split('_')[0])
TrueSlices=int((range2/step)+1);    
base_img=nib.load(C1_name)
base_img=np.squeeze(np.asarray(base_img.get_fdata(),dtype='uint16')).transpose()        
C1frames=np.zeros((int(len(MC_img_list)),TrueSlices,base_img.shape[1],base_img.shape[2]), dtype='uint16')
for img_nb,C2_name in enumerate(MC_img_list):    
 img_nb=int( re.search('_power.+_(\d+)\.tif',C2_name).group(1)) 
 try:
  img_temp=nib.load(C2_name)
  img_temp=img_temp.get_fdata()
 except:
  Register_single_image_noMask_SecondPass(C2_name.replace('_Greedy2.nii',''),template_name)
  img_temp=nib.load(C1_name)
  img_temp=img_temp.get_fdata()    
 img_temp=np.squeeze(np.asarray(img_temp,dtype='uint16')).transpose()
 C1frames[img_nb,:,:,:]=img_temp 
 tifffile.imwrite(tif_file_folder+'/'+file_name+'_4D2.tif',C1frames)

print(tif_file_folder + 'is done')