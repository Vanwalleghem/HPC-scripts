import tifffile
import numpy as np
import os
import sys
import glob
import nibabel as nib
import re

tif_file_folder=sys.argv[1]
file_name=os.path.basename(os.path.normpath(tif_file_folder))
range2=int(file_name.split('range')[-1].split('_')[0])
step=int(file_name.split('step')[-1].split('_')[0])
TrueSlices=int((range2/step)+1);    
 
MC_img_list=glob.glob(tif_file_folder+'/3Dreg/*'+os.path.basename(os.path.normpath(tif_file_folder))+'*_Warped3.nii.gz')
print(tif_file_folder+' '+str(len(MC_img_list)))
file_name=os.path.basename(os.path.normpath(tif_file_folder))

if len(MC_img_list)<1200:
  print('Not all files were processed')
  break
else:
 C1_name=MC_img_list[0] 
 try:
  base_img=nib.load(C1_name)
 except:
  print('error in loading the image')
 base_img=np.squeeze(np.asarray(base_img.get_fdata(dtype='float16'),dtype='uint16')).transpose()        
 ImgData=np.zeros((TrueSlices,base_img.shape[1],base_img.shape[2]), dtype='uint16')
 ImgTimeMax=np.zeros((int(len(MC_img_list)),base_img.shape[1],base_img.shape[2]), dtype='uint16')
 for img_nb,C2_name in enumerate(MC_img_list):    
  img_nb=int( re.search('_power.+_time(\d+)\.tif.',C2_name).group(1)) 
  try:
   img_temp=nib.load(C2_name)
   img_temp=img_temp.get_fdata(dtype='float16')
  except:
   print('error loading ' + C2_name)
  img_temp=np.squeeze(np.asarray(img_temp,dtype='uint16')).transpose()
  C1frames[img_nb,:,:,:]=img_temp 
 #tifffile.imwrite(tif_file_folder+'/'+file_name+'_4D.tif',C1frames)
 tifffile.imwrite(tif_file_folder+'/'+file_name+'_4D2_MaxZ.tif',np.max(C1frames,axis=1))
 tifffile.imwrite(tif_file_folder+'/'+file_name+'_4D2_MeanT.tif',np.mean(C1frames,axis=0))
 print(tif_file_folder + 'is done') 


ImgMax=tifffile.imread(List_files[0]) 
for file_name in List_files:
 ImgData=tifffile.imread(file_name) 
 ImgMax=np.max(np.stack((ImgData,ImgMax)), axis=0)

file_name=os.path.basename(os.path.normpath(tif_file_folder))               
tifffile.imwrite('/faststorage/project/FUNCT_ENS/Max/'+file_name+'_Max.tif',np.transpose(ImgMax,(2,0,1)))
tifffile.imwrite('/faststorage/project/FUNCT_ENS/Max/'+file_name+'_MaxMax.tif',np.max(ImgMax, axis=0))


