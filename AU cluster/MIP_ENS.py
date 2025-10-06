import tifffile
import numpy as np
import os
import sys
import glob

tif_file_folder=sys.argv[1]
file_name=os.path.basename(os.path.normpath(tif_file_folder))
range2=int(file_name.split('range')[-1].split('_')[0])
step=int(file_name.split('step')[-1].split('_')[0])
TrueSlices=int((range2/step)+1);    



List_files=sorted(glob.glob(os.path.join(tif_file_folder,'3Dreg/*Warped3*.tif')))
if len(List_files)<1200:
 List_files=sorted(glob.glob(os.path.join(tif_file_folder,'3Dreg/*Warped2*.tif')))

ImgMax=tifffile.imread(List_files[0]) 
for file_name in List_files:
 ImgData=tifffile.imread(file_name) 
 ImgMax=np.max(np.stack((ImgData,ImgMax)), axis=0)

file_name=os.path.basename(os.path.normpath(tif_file_folder))               
tifffile.imwrite('/faststorage/project/FUNCT_ENS/Max/'+file_name+'_Max.tif',np.transpose(ImgMax,(2,0,1)))
tifffile.imwrite('/faststorage/project/FUNCT_ENS/Max/'+file_name+'_MaxMax.tif',np.max(ImgMax, axis=0))