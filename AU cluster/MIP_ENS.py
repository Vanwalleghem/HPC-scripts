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
dims=np.asarray(ImgData.shape) #time should be the largest dimension
ImgMax=np.max(ImgData, axis=np.argmax(dims))
tifffile.imwrite('/faststorage/project/FUNCT_ENS/Max/'+file_name+'_Max.tif',ImgMax) #You need to make sure you save to a folder you have access to
dims=np.asarray(ImgMax.shape) #time should be the largest dimension
ImgMax=np.max(ImgMax, axis=np.argmin(dims)) #z-axis should be the smallest
tifffile.imwrite('/faststorage/project/FUNCT_ENS/Max/'+file_name+'_MaxMax.tif',ImgMax) #You need to make sure you save to a folder you have access to