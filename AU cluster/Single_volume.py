import tifffile
import numpy as np
import os
import sys

tif_file_folder=sys.argv[1]
file_name=os.path.basename(os.path.normpath(tif_file_folder))
range2=int(file_name.split('range')[-1].split('_')[0])
step=int(file_name.split('step')[-1].split('_')[0])
TrueSlices=int((range2/step)+1);    

ImgData=tifffile.imread(tif_file_folder+'/'+file_name+'_4D2.tif')
ImgSingle=ImgData[0:500:50,:,:,:].transpose(0,3,1,2) 
tifffile.imwrite('/faststorage/project/FUNCT_ENS/Max/_Single_'+file_name+'.ome.tif',ImgSingle, metadata={'axes': 'TZYX'})