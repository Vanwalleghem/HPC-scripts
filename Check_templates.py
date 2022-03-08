from subprocess import call
import time
import glob
import os
import sys
import tifffile
from skimage import io
import numpy as np
import nibabel as nib
import multiprocessing as mp
from scipy import signal
import gc

def is_file_empty(file_path):
 """ Check if file is empty by confirming if its size is 0 bytes"""
 # Check if file exist and it is empty    
 if os.path.exists(file_path):
  if os.stat(file_path).st_size == 0:
   return True
  else:
   return False
 else:
  return True 
    
def CheckTemplate(tif_file_folder):
 if not is_file_empty(tif_file_folder+'/3Dreg/template.tif'):
  temp=tifffile.imread(tif_file_folder+'/3Dreg/template.tif')
  if not len(temp.shape)==3:
   MakeTemplate(tif_file_folder)
  else:
   print('Template is OK')
 else:     
  MakeTemplate(tif_file_folder)
  
def MakeTemplate(tif_file_folder):
 tif_list=glob.glob(tif_file_folder+'/*.tif')
 tif_list.sort()
 temp=[]
 for idx_nb,file in enumerate(tif_list):
  if idx_nb==0:
   temp=io.imread(file,plugin='pil')
  else:
   temp=np.concatenate((temp,io.imread(file,plugin='pil')),axis=0)  
 file_name=tif_file_folder.split('/')[-1]
 range2=int(file_name.split('range')[-1].split('_')[0])
 step=int(file_name.split('step')[-1].split('_')[0])
 TrueSlices=(range2/step)+1;
 dims=temp.shape
 temp=np.reshape(temp,[dims[0]/TrueSlices,TrueSlices,dims[1],dims[2]])

 #Computing the difference between points from frame to frame should give the point with least changes
 #std_movie=temp[:,0:200].std(axis=(2,3))
 number_of_frames_to_check=50
 std_movie=np.diff(temp[0:number_of_frames_to_check].reshape([number_of_frames_to_check,temp.shape[1],temp.shape[2]*temp.shape[3]]),axis=-1)
 idx_template=np.argmin(std_movie,axis=0)
 #ignores the 0s and compute the mean index of the lowest changes
 idx_template=int(idx_template[idx_template>0].ravel().mean())
 
 #tmp_idx=np.argmin(signal.detrend(std_movie))
 #mean image of the 3 points surrounding the minimum movement
 template=temp[idx_template-1:idx_template+2].mean(axis=0)
 directory = os.getcwd()
 try:
  new_dir=tif_file_folder+'/3Dreg'
  os.mkdir(new_dir)
 except:
  print('directory exists') 
 os.chdir(new_dir)
 template_name=new_dir+'/template.tif'
 tifffile.imsave(template_name,template.astype(np.uint16)) 
 del temp,std_movie
 print('New template created')
 gc.collect()


tif_file_folder=sys.argv[1]
os.chdir(os.path.dirname(tif_file_folder))
template_name=tif_file_folder+'/3Dreg/template.tif'
call(['/usr/local/bin/recall_medici '+template_name],shell=True)

CheckTemplate(tif_file_folder)
