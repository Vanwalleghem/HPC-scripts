import tifffile
import numpy as np
import os
import sys
import glob
from skimage import io

def MakeListAndStacks(tif_file_folder):
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

tif_file_folder=sys.argv[1]
file_name=os.path.basename(os.path.normpath(tif_file_folder))
#range2=int(file_name.split('range')[-1].split('_')[0])
#step=int(file_name.split('step')[-1].split('_')[0])
#TrueSlices=int((range2/step)+1);

tif_list=glob.glob(tif_file_folder+'/3Dreg/*.tif')
if len(tif_list)==0:
 MakeListAndStacks(tif_file_folder)
 tif_list=glob.glob(tif_file_folder+'/3Dreg/*.tif')
 
tif_list.sort()
temp=tifffile.imread(tif_list[0])
dims=temp.shape
temp=np.zeros([len(tif_list),dims[1],dims[2]],dtype='uint16')

for idx_nb,file_name in enumerate(tif_list):
 img=tifffile.imread(file_name)
 ImgMax=np.max(img, axis=0)
 temp[idx_nb,:,:]=ImgMax
    #if idx_nb==0:
    #    temp=io.imread(file,plugin='pil')
    #else:
    #    temp=np.concatenate((temp,io.imread(file,plugin='pil')),axis=0)
    
#file_name=tif_file_folder.split('/')[-1]
#range2=int(file_name.split('range')[-1].split('_')[0])
#step=int(file_name.split('step')[-1].split('_')[0])
#TrueSlices=(range2/step)+1;
#dims=temp.shape
#temp=np.reshape(temp,[dims[0]/TrueSlices,TrueSlices,dims[1],dims[2]])
file_name=os.path.basename(os.path.normpath(tif_file_folder))
tifffile.imwrite('/faststorage/project/Student_ENS/Pierre/'+file_name+'_Max.tif',temp)