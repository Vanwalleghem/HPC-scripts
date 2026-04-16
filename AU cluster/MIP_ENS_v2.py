import tifffile
import numpy as np
import os
import sys
import glob
import re

tif_file_folder=sys.argv[1]
file_name=os.path.basename(os.path.normpath(tif_file_folder))
range2=int(file_name.split('range')[-1].split('_')[0])
step=int(file_name.split('step')[-1].split('_')[0])
TrueSlices=int((range2/step)+1);    

MC_img_list=sorted(glob.glob(os.path.join(tif_file_folder,'3Dreg/GV*Warped3.tif')))
if len(MC_img_list)<1200:
 print('not enough warped3.tif files, switching to warped2')
 #List_files=sorted(glob.glob(os.path.join(fnames[0],'3Dreg/*Warped2*.tif')))
 MC_img_list=sorted(glob.glob(os.path.join(tif_file_folder,'3Dreg/GV*Warped2.tif')))

print(tif_file_folder+' '+str(len(MC_img_list)))
file_name=os.path.basename(os.path.normpath(tif_file_folder))

C1_name=MC_img_list[0] 
base_img=tifffile.imread(C1_name)
ImgTimeMax=np.zeros((640,540,int(len(MC_img_list))), 'uint16')
for C2_name in MC_img_list:
 try:
  img_nb=int( re.search(r'_power.+_(\d+).tif.+',C2_name).group(1))
 except:
  print('error in filename: ' + C2_name) 
 try:
  img_temp=tifffile.imread(C2_name)
 except:
  print('error loading ' + C2_name) 
 ImgTimeMax[:,:,img_nb]=img_temp.max(axis=-1)

tifffile.imwrite('/faststorage/project/FUNCT_ENS/Max/'+file_name+'_Max.tif',ImgTimeMax)