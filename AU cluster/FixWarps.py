# -*- coding: utf-8 -*-
"""
Created on Wed Jan  7 11:42:10 2026

@author: au691573
"""
import tifffile
import numpy as np
import os
import glob
import re
tif_file_folders=glob.glob(os.path.join('/faststorage/project/FUNCT_ENS/NewENSDataDK','**/3Dreg/'),recursive=True)

for tif_file_folder in tif_file_folders:
    file_name=os.path.basename(os.path.normpath(tif_file_folder.split('3Dreg')[0]))
    if not os.path.exists(os.path.join('/faststorage/project/FUNCT_ENS/MaxTime',file_name+'_Warp3_MaxZ.tif')):
        MC_img_list=glob.glob(os.path.join(tif_file_folder,'*_Warped3.tif'))
        print(tif_file_folder+' '+str(len(MC_img_list)))    
        
        if len(MC_img_list)<1200:
          print('Not all files were processed')
          continue
        else:
            C1_name=MC_img_list[0] 
            base_img=tifffile.imread(C1_name)     
            ImgTimeMax=np.zeros((int(len(MC_img_list)),base_img.shape[0],base_img.shape[1]), dtype='uint16')
            for img_nb,C2_name in enumerate(MC_img_list):    
             img_nb=int( re.search(r'_power.+_time(\d+)\.tif.',C2_name).group(1)) 
             img_temp=tifffile.imread(C2_name)    
             ImgTimeMax[img_nb,:,:]=np.max(img_temp,axis=-1) 
        
        
        tifffile.imwrite(os.path.join('/faststorage/project/FUNCT_ENS/MaxTime',file_name+'_Warp3_MaxZ.tif'),ImgTimeMax)
