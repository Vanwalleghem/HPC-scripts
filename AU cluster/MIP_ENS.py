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
ImgMax=np.max(ImgData, axis=1)
tifffile.imwrite(tif_file_folder+'/'+file_name+'_Max.tif',ImgMax)