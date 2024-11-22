import glob
import os
import tifffile
import numpy as np
from subprocess import call
import nibabel as nib
import sys

def Warp_image_Twice(Mov_name):
    Warping_matrix = Mov_name.replace('.tif','_Greedy.nii.gz')
    Affine_name = Mov_name.replace('.tif','_Greedy_affine.mat')
    job_string = "greedy -d 3 -rf FixImg -rm MovImg MovImg_Warped.nii.gz -r OutImg Affine_name"
    job_string = job_string.replace('Affine_name',Affine_name).replace('OutImg',Warping_matrix).replace('FixImg',Mov_name).replace('MovImg',Mov_name)
    call(job_string,shell=True)
    Warping_matrix2 = Mov_name.replace('.tif','_Greedy2.nii.gz')
    job_string = "greedy -d 3 -rf FixImg -rm MovImg_Warped.nii.gz MovImg_Warped2.nii.gz -r OutImg_Greedy2.nii.gz"
    job_string = job_string.replace('OutImg',Mov_name).replace('FixImg',Mov_name).replace('MovImg',Mov_name)
    call(job_string,shell=True)
    
def Warp_image_second(Mov_name): #Mov_name ends in _Warped.nii.gz
    Warping_matrix2 = Mov_name.replace('_Warped.nii.gz','_Greedy2.nii.gz')
    job_string = "greedy -d 3 -rf FixImg -rm MovImg MovWarped -r WarpImg"
    job_string = job_string.replace('WarpImg',Warping_matrix2).replace('FixImg',Mov_name).replace('MovWarped',Mov_name.replace('_Warped','_Warped2')).replace('MovImg',Mov_name)
    call(job_string,shell=True)

tif_file_folder=sys.argv[1]
tif_file_folder=os.path.normpath(tif_file_folder)
file_name=os.path.basename(tif_file_folder)

img_list=glob.glob(tif_file_folder+'/3Dreg/*'+os.path.basename(os.path.normpath(tif_file_folder))+'*_Warped.nii.gz')
for img in img_list:
    Warp_image_second(img)

MC_img_list=glob.glob(tif_file_folder+'/3Dreg/*'+os.path.basename(os.path.normpath(tif_file_folder))+'*_Warped2.nii.gz')    
print(tif_file_folder+' '+str(len(MC_img_list)))    
file_name=os.path.basename(os.path.normpath(tif_file_folder))
if len(MC_img_list)==1200:
 C1_name=MC_img_list[0] 
 range2=int(file_name.split('range')[-1].split('_')[0])
 step=int(file_name.split('step')[-1].split('_')[0])
 TrueSlices=int((range2/step)+1);    
 try:
  base_img=nib.load(C1_name)
 except:
  print("error in loading the file: "+C1_name)
  base_img=nib.load(C1_name)
 base_img=np.squeeze(np.asarray(base_img.get_fdata(),dtype='uint16')).transpose()        
 C1frames=np.zeros((int(len(MC_img_list)),TrueSlices,base_img.shape[1],base_img.shape[2]), dtype='uint16')
 for img_nb,C2_name in enumerate(MC_img_list):    
  img_nb=int( re.search('_power.+_time(\d+)\.tif',C2_name).group(1)) 
  try:
   img_temp=nib.load(C2_name)
   img_temp=img_temp.get_fdata()
  except:
   print("error in loading the file: "+C2_name)
  img_temp=np.squeeze(np.asarray(img_temp,dtype='uint16')).transpose()
  C1frames[img_nb,:,:,:]=img_temp 
 tifffile.imwrite(tif_file_folder+'/'+file_name+'_4D2.tif',C1frames)
 tifffile.imwrite(tif_file_folder+'/'+file_name+'_4D2_MaxZ.tif',np.max(C1frames,axis=1)) 
 print(tif_file_folder + 'is done')