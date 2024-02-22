import glob
import os
import sys
import tifffile
from skimage import io
import numpy as np

def MakeListAndStacksAndMIP(tif_file_folder):
 tif_list=glob.glob(tif_file_folder+'/Default/*.tif')
 time_list=list(set([file_name.split('time')[-1].split('_')[0] for file_name in tif_list]))
 time_list.sort()
 file_name=os.path.dirname(tif_file_folder)
 if file_name=='' or os.path.isdir(file_name):
  file_name=os.path.basename(os.path.dirname(tif_file_folder))
 try:
  new_dir=tif_file_folder+'/3Dreg'
  os.mkdir(new_dir)
 except:
  print('directory exists')
 tif_list_time=glob.glob(new_dir+'*_time*.tif') 
 if len(tif_list_time)==len(time_list):
  return
 for time in time_list:
  file_names=[file_name for file_name in tif_list if file_name.split('time')[-1].split('_')[0]==time]
  temp=tifffile.imread(file_names[0])
  dims=temp.shape
  temp=np.zeros([len(file_names),dims[0],dims[1],],dtype='uint16')
  for idx_nb,file in enumerate(file_names): 
   temp[idx_nb,:,:]=tifffile.imread(file)
  tifffile.imwrite(os.path.join(new_dir,file_name)+'_time'+time+'.tif',temp.astype(np.uint16))
  #Delete the 4 lines below if it bugs out, this is an attempt at making the MIP at the same time
  if time==0:
   ImgMax=np.max(temp, axis=0)
  else:
   ImgMax=np.max(np.stack((ImgMax,np.max(temp, axis=0)), axis=0))  
  tifffile.imwrite(tif_file_folder+'/'+file_name+'_Max.tif',ImgMax)
  

tif_file_folder=sys.argv[1]
tif_list=MakeListAndStacksAndMIP(tif_file_folder)
img_seq_list=glob.glob(tif_file_folder+'/3Dreg/*_time*.tif')


