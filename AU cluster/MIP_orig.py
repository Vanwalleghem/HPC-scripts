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
 
MC_img_list=glob.glob(os.path.join(tif_file_folder,'3Dreg','*RS*.tif'))
MC_img_list=[x for x in MC_img_list if 'arped' not  in x]

print(tif_file_folder+' '+str(len(MC_img_list)))
file_name=os.path.basename(os.path.normpath(tif_file_folder))

base_img=tifffile.imread(MC_img_list[0])
ImgData=np.zeros((TrueSlices,base_img.shape[1],base_img.shape[2]), dtype='uint16')
for file_name in MC_img_list:
    img_data=tifffile.imread(file_name)
    ImgData=np.maximum(ImgData,img_data)


tifffile.imwrite(os.path.join(tif_file_folder,file_name+'_orig_MaxT.tif'),ImgData)
