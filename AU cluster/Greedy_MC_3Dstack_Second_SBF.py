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
import re
import nrrd

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

def Register_single_image_noMask_SecondPass(Mov_name,template_name):        
    output_name = Mov_name.replace('_Warped.nii','_Greedy2')    
    if is_file_empty(output_name+'.nii'):
        job_string = "greedy -d 3 -o OutImg.nii -i FixImg MovImg -sv -n 200x100x50 -e 0.25 -m NCC 2x2x2"
        job_string = job_string.replace('OutImg',output_name).replace('FixImg',template_name).replace('MovImg',Mov_name)
        call([job_string],shell=True)          
    output_image = Mov_name.replace('_Warped.nii','_Warped2')
    if is_file_empty(output_image+'.nii'):    
        job_string = "greedy -d 3 -rf FixImg -rm MovImg OutImg.nii -r "+output_name+'.nii'
        job_string = job_string.replace('OutImg',output_image).replace('FixImg',template_name).replace('MovImg',Mov_name)
        call([job_string],shell=True)
        
def Register_single_image_SecondPass(Mov_name,template_name,Mask_name):        
 output_name = Mov_name.replace('_Warped.nii','_Greedy2')
 if is_file_empty(output_name+'.nii'):   
  job_string = "greedy -d 3 -float -o OutImg.nii -i FixImg MovImg -gm MaskImg -n 200x100x50 -e 0.25 -m NCC 2x2x2"
  job_string = job_string.replace('OutImg',output_name).replace('FixImg',template_name).replace('MovImg',Mov_name).replace('MaskImg',Mask_name)
  call([job_string],shell=True)          
 output_image = Mov_name.replace('_Warped.nii','_Warped2')
 if is_file_empty(output_name+'.nii'):
  job_string = "greedy -d 3 -rf FixImg -rm MovImg OutImg.nii -r "+output_name+'.nii'
  job_string = job_string.replace('OutImg',output_image).replace('FixImg',template_name).replace('MovImg',Mov_name).replace('MaskImg',Mask_name)
  call([job_string],shell=True)
    
def Register_single_image(Mov_name,template_name,Mask_name):        
    output_name = Mov_name.replace('.tif','_Greedy')
    Affine_name = Mov_name.replace('.tif','_Greedy_affine.mat')
    if not os.path.exists(output_name+'_Greedy_affine.mat') and is_file_empty(output_name+'.nii'):        
        output_name = Mov_name.replace('.tif','_Greedy') 
        Affine_name = Mov_name.replace('.tif','_Greedy_affine.mat')
        job_string = "greedy -d 3 -a -float -o Affine_name -i FixImg MovImg -gm MaskImg -n 100x40x20 -e 0.25 -ia-image-centers -m NCC 2x2x2"
        job_string = job_string.replace('Affine_name',Affine_name).replace('OutImg',output_name).replace('FixImg',template_name).replace('MovImg',Mov_name).replace('MaskImg',Mask_name)
        call([job_string],shell=True)  
        print(job_string)
        job_string = "greedy -d 3 -float -o OutImg.nii -i FixImg MovImg -gm MaskImg -it Affine_name -n 100x50x20 -e 0.25 -m NCC 2x2x2"
        job_string = job_string.replace('Affine_name',Affine_name).replace('OutImg',output_name).replace('FixImg',template_name).replace('MovImg',Mov_name).replace('MaskImg',Mask_name)
        call([job_string],shell=True)  
        job_string = "greedy -d 3 -rf FixImg -rm MovImg MovImg_Warped.nii -r OutImg.nii Affine_name"
        job_string = job_string.replace('Affine_name',Affine_name).replace('OutImg',output_name).replace('FixImg',template_name).replace('MovImg',Mov_name).replace('MaskImg',Mask_name)
        call([job_string],shell=True)

def Register_single_image_forced(Mov_name,template_name,Mask_name):        
    output_name = Mov_name.replace('.tif','_Greedy') 
    Affine_name = Mov_name.replace('.tif','_Greedy_affine.mat')
    job_string = "greedy -d 3 -a -float -o Affine_name -i FixImg MovImg -gm MaskImg -n 100x40x20 -e 0.25 -ia-image-centers -m NCC 2x2x2"
    job_string = job_string.replace('Affine_name',Affine_name).replace('OutImg',output_name).replace('FixImg',template_name).replace('MovImg',Mov_name).replace('MaskImg',Mask_name)
    call([job_string],shell=True)  
    print(job_string)
    job_string = "greedy -d 3 -float -o OutImg.nii -i FixImg MovImg -gm MaskImg -it Affine_name -n 100x50x20 -e 0.25 -m NCC 2x2x2"
    job_string = job_string.replace('Affine_name',Affine_name).replace('OutImg',output_name).replace('FixImg',template_name).replace('MovImg',Mov_name).replace('MaskImg',Mask_name)
    call([job_string],shell=True)  
    job_string = "greedy -d 3 -rf FixImg -rm MovImg MovImg_Warped.nii -r OutImg.nii Affine_name"
    job_string = job_string.replace('Affine_name',Affine_name).replace('OutImg',output_name).replace('FixImg',template_name).replace('MovImg',Mov_name).replace('MaskImg',Mask_name)
    call([job_string],shell=True)

def MakeListAndHyperstack(tif_file_folder):
    tif_list=glob.glob(tif_file_folder+'/*_Warped.nii')
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

tif_file_folder=sys.argv[1]
tif_file_folder=os.path.normpath(tif_file_folder)
print(tif_file_folder)
os.chdir(os.path.dirname(tif_file_folder))
img_seq_list=glob.glob(tif_file_folder+'/3Dreg/*_Warped.nii.gz')
template_name=tif_file_folder+'/3Dreg/template.tif'
mask_name='/faststorage/project/FUNCT_ENS/TemplateFiles/Done/'+os.path.basename(tif_file_folder).split('_range')[0]+'_template.tif'
for img_name in img_seq_list:
 Register_single_image_SecondPass(img_name,template_name,mask_name)
 print(img_name)

MC_img_list=glob.glob(tif_file_folder+'/3Dreg/*'+os.path.basename(os.path.normpath(tif_file_folder))+'*_Warped2.nii')    
#MC_img_list=[x for x in MC_img_list if not 'LongReg' in x]
print(tif_file_folder+' '+str(len(MC_img_list)))    
file_name=os.path.basename(os.path.normpath(tif_file_folder))
if len(MC_img_list)==1200 and not os.path.exists(tif_file_folder+'/'+file_name+'_4D2.tif'):
 C1_name=MC_img_list[0] 
 range2=int(file_name.split('range')[-1].split('_')[0])
 step=int(file_name.split('step')[-1].split('_')[0])
 TrueSlices=int((range2/step)+1);    
 try:
  base_img=nib.load(C1_name)
 except:
  Register_single_image_SecondPass(C1_name.replace('_Greedy2.nii',''),template_name,mask_name)
  base_img=nib.load(C1_name)
 base_img=np.squeeze(np.asarray(base_img.get_fdata(),dtype='uint16')).transpose()        
 C1frames=np.zeros((int(len(MC_img_list)),TrueSlices,base_img.shape[1],base_img.shape[2]), dtype='uint16')
 for img_nb,C2_name in enumerate(MC_img_list):    
  img_nb=int( re.search('_power.+_(\d+)\.tif',C2_name).group(1)) 
  try:
   img_temp=nib.load(C2_name)
   img_temp=img_temp.get_fdata()
  except:
   Register_single_image_SecondPass(C2_name.replace('_Greedy2.nii',''),template_name,mask_name)
   img_temp=nib.load(C1_name)
   img_temp=img_temp.get_fdata()    
  img_temp=np.squeeze(np.asarray(img_temp,dtype='uint16')).transpose()
  C1frames[img_nb,:,:,:]=img_temp 
 tifffile.imwrite(tif_file_folder+'/'+file_name+'_4D2.tif',C1frames)
 #nrrd.write(tif_file_folder+'/'+file_name+'_4D.nrrd',C1frames)   
 print(tif_file_folder + 'is done')
else:
 test=[x.split('_Greedy2.nii')[0] for x in MC_img_list]
 test=set(test) ^ set(img_seq_list)
 for img_name in test:
  Register_single_image_SecondPass(img_name,template_name,mask_name)
  print(img_name)
