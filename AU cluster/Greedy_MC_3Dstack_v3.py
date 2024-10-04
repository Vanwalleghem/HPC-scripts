from subprocess import call
import time
import glob
import os
import sys
import tifffile
from skimage import io
import numpy as np
import nibabel as nib
from scipy import signal
import gc
import re

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
    
def Register_single_image(Mov_name,template_name,Mask_name):        
    output_name = Mov_name.replace('.tif','_Greedy')
    Affine_name = Mov_name.replace('.tif','_Greedy_affine.mat')
    if not os.path.exists(output_name+'_Greedy_affine.mat') and is_file_empty(output_name+'.nii.gz'):        
        output_name = Mov_name.replace('.tif','_Greedy') 
        Affine_name = Mov_name.replace('.tif','_Greedy_affine.mat')
        job_string = "greedy -d 3 -a -o Affine_name -i FixImg MovImg -gm MaskImg -n 200x80x40 -e 0.4 -ia-image-centers -m NCC 3x3x2"
        job_string = job_string.replace('Affine_name',Affine_name).replace('OutImg',output_name).replace('FixImg',template_name).replace('MovImg',Mov_name).replace('MaskImg',Mask_name)
        call([job_string],shell=True)  
        print(job_string)
        job_string = "greedy -d 3 -o OutImg.nii.gz -i FixImg MovImg -gm MaskImg -it Affine_name -n 200x80x40 -e 0.4 -m NCC 3x3x2"
        job_string = job_string.replace('Affine_name',Affine_name).replace('OutImg',output_name).replace('FixImg',template_name).replace('MovImg',Mov_name).replace('MaskImg',Mask_name)
        call([job_string],shell=True)  
        job_string = "greedy -d 3 -rf FixImg -rm MovImg MovImg_Warped.nii.gz -r OutImg.nii.gz Affine_name"
        job_string = job_string.replace('Affine_name',Affine_name).replace('OutImg',output_name).replace('FixImg',template_name).replace('MovImg',Mov_name).replace('MaskImg',Mask_name)
        call([job_string],shell=True)

def Register_single_image_forced(Mov_name,template_name,Mask_name):        
    output_name = Mov_name.replace('.tif','_Greedy').replace('3Dreg','3Dreg2')
    Affine_name = Mov_name.replace('.tif','_Greedy_affine.mat')
    job_string = "greedy -d 3 -a -o Affine_name -i FixImg MovImg -gm MaskImg -n 200x80x40 -e 0.4 -ia-image-centers -m NCC 3x3x2"
    job_string = job_string.replace('Affine_name',Affine_name).replace('OutImg',output_name).replace('FixImg',template_name).replace('MovImg',Mov_name).replace('MaskImg',Mask_name)
    call([job_string],shell=True)  
    print(job_string)
    job_string = "greedy -d 3 -o OutImg.nii.gz -i FixImg MovImg -gm MaskImg -it Affine_name -n 200x80x40 -e 0.4 -m NCC 3x3x2"
    job_string = job_string.replace('Affine_name',Affine_name).replace('OutImg',output_name).replace('FixImg',template_name).replace('MovImg',Mov_name).replace('MaskImg',Mask_name)
    call([job_string],shell=True)  
    job_string = "greedy -d 3 -rf FixImg -rm MovImg MovImg_Warped.nii.gz -r OutImg.nii.gz Affine_name"
    job_string = job_string.replace('Affine_name',Affine_name).replace('OutImg',output_name).replace('FixImg',template_name).replace('MovImg',Mov_name).replace('MaskImg',Mask_name)
    call([job_string],shell=True)

def MakeListAndHyperstack(tif_file_folder):
    tif_list=glob.glob(tif_file_folder+'/*.tif')
    tif_list.sort()
    if not (os.path.exists(tif_file_folder+'/3Dreg/template.tif') and not is_file_empty(tif_file_folder+'/3Dreg/'+tif_file_folder.split('/')[-2]+'_0.tif')):
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
        img_seq_list=list()
         
        for img_nb in range(0,temp.shape[0]):
            img_name=new_dir+'/'+tif_file_folder.split('/')[-1]+'_'+str(img_nb)+'.tif'
            tifffile.imsave(img_name,temp[img_nb].astype(np.uint16))
            img_seq_list.append(img_name)
        del temp,std_movie
        gc.collect()
    return(tif_list)
    
def FindTemplate(tif_file_folder,number_of_frames_to_check=50):
    new_dir=tif_file_folder+'/3Dreg/'
    tif_list_time=sorted(glob.glob(new_dir+'*_time*.tif'))
    for idx_nb in range(0,number_of_frames_to_check):
        file = tif_list_time[idx_nb]
        if idx_nb==0:
            temp=io.imread(file,plugin='pil')
        else:
            temp=np.concatenate((temp,io.imread(file,plugin='pil')),axis=0)
    std_movie=np.diff(temp[0:number_of_frames_to_check].reshape([number_of_frames_to_check,temp.shape[1],temp.shape[2]*temp.shape[3]]),axis=-1)
    idx_template=np.argmin(std_movie,axis=0)
    return(tif_list_time[idx_template])
    
def MakeListAndStacks(tif_file_folder):
 tif_list=glob.glob(tif_file_folder+'/Default/*.tif')
 time_list=list(set([file_name.split('time')[-1].split('_')[0] for file_name in tif_list]))
 time_list.sort()
 file_name=os.path.basename(tif_file_folder)
 if file_name=='' or os.path.isdir(file_name):
  file_name=os.path.basename(os.path.dirname(tif_file_folder))
 try:
  new_dir=tif_file_folder+'/3Dreg'
  os.mkdir(new_dir)
 except:
  print('directory exists')
 tif_list_time=glob.glob(new_dir+'*_time*.tif') 
 if len(tif_list_time)==len(time_list):
  print('directory already processed')
  return
 for count,time in enumerate(time_list):
  file_names=[file_name for file_name in tif_list if file_name.split('time')[-1].split('_')[0]==time]
  file_names.sort()
  if count==0:
   temp=tifffile.imread(file_names[0])
   dims=temp.shape
   temp=np.zeros([len(file_names),dims[0],dims[1]],dtype='uint16')
  for idx_nb,file in enumerate(file_names): 
   temp[idx_nb,:,:]=tifffile.imread(file)
  tifffile.imwrite(os.path.join(new_dir,file_name)+'_time'+time+'.tif',temp.astype(np.uint16))

tif_file_folder=sys.argv[1]
tif_list=MakeListAndStacks(tif_file_folder)
tif_file_folder=os.path.normpath(tif_file_folder)
print(tif_file_folder)
img_seq_list=glob.glob(tif_file_folder+'/3Dreg/*.tif')

#Need to change to match your naming scheme
file_name=os.path.basename(tif_file_folder)
if file_name=='' or os.path.isdir(file_name):
 file_name=os.path.basename(os.path.dirname(tif_file_folder))
mask_name=os.path.join(tif_file_folder,file_name.split('_range')[0]+'_template.tif')
mask_check=tifffile.imread(mask_name)
if len(mask_check.shape)==2:
 dims=mask_check.shape 
 range2=int(file_name.split('range')[-1].split('_')[0])
 step=int(file_name.split('step')[-1].split('_')[0])
 TrueSlices=int((range2/step)+1);
 fixed_mask=np.zeros([TrueSlices,dims[0],dims[1]],dtype='uint16')
 for i in range(0,TrueSlices):
  fixed_mask[i,:,:]=mask_check
 tifffile.imwrite(mask_name,fixed_mask.astype(np.uint16))

#template_name=FindTemplate(tif_file_folder)
template_name=img_seq_list[0]

for img_name in img_seq_list:
 Register_single_image(img_name,template_name,mask_name)
 print(img_name)

MC_img_list=glob.glob(tif_file_folder+'/3Dreg/*'+os.path.basename(os.path.normpath(tif_file_folder))+'*_Warped.nii.gz')    
print(tif_file_folder+' '+str(len(MC_img_list)))    
f = open(tif_file_folder+'/ListOfFailedFiles.txt','w')
file_name=os.path.basename(os.path.normpath(tif_file_folder))
if len(MC_img_list)==1200 and not os.path.exists(tif_file_folder+'/'+file_name+'_4D.tif'):
 C1_name=MC_img_list[0] 
 range2=int(file_name.split('range')[-1].split('_')[0])
 step=int(file_name.split('step')[-1].split('_')[0])
 TrueSlices=int((range2/step)+1);    
 try:
  base_img=nib.load(C1_name)
 except:
  Register_single_image_forced(C1_name.replace('_Warped.nii.gz',''),template_name,mask_name)
  base_img=nib.load(C1_name)
 base_img=np.squeeze(np.asarray(base_img.get_fdata(dtype='float16'),dtype='uint16')).transpose()        
 C1frames=np.zeros((int(len(MC_img_list)),TrueSlices,base_img.shape[1],base_img.shape[2]), dtype='uint16')
 for img_nb,C2_name in enumerate(MC_img_list):    
  img_nb=int( re.search('_power.+_(\d+)\.tif',C2_name).group(1)) 
  try:
   img_temp=nib.load(C2_name)
   img_temp=img_temp.get_fdata(dtype='float16')
  except:
   Register_single_image_forced(C2_name.replace('_Warped.nii.gz',''),template_name,mask_name)
   img_temp=nib.load(C1_name)
   img_temp=img_temp.get_fdata(dtype='float16')    
  img_temp=np.squeeze(np.asarray(img_temp,dtype='uint16')).transpose()
  C1frames[img_nb,:,:,:]=img_temp 
 tifffile.imwrite(tif_file_folder+'/'+file_name+'_4D.tif',C1frames)
 tifffile.imwrite(tif_file_folder+'/'+file_name+'_4D_MaxZ.tif',np.max(C1frames,axis=1))
 tifffile.imwrite(tif_file_folder+'/'+file_name+'_4D_MeanT.tif',np.mean(C1frames,axis=0))
 print(tif_file_folder + 'is done')
else:
 test=[x.split('_Warped.nii.gz')[0] for x in MC_img_list]
 test=set(test) ^ set(img_seq_list)
 for img_name in test:
  Register_single_image_forced(img_name,template_name,mask_name)
  print(img_name)
