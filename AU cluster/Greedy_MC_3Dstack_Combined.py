from subprocess import call
import glob
import os
import sys
import tifffile
from skimage import io
import numpy as np
import nibabel as nib
import re
import natsort

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

def Register_single_image_SecondPass(Mov_name,template_name,Mask_name):        
 output_name = Mov_name.replace('_Warped.nii.gz','_Greedy2').replace('_Greedy.nii.gz','_Greedy2')
 if is_file_empty(output_name+'.nii.gz'):   
  job_string = "greedy -d 3 -float -o OutImg.nii.gz -i FixImg MovImg -gm MaskImg -n 200x100x50 -e 0.25 -m NCC 2x2x2"
  job_string = job_string.replace('OutImg',output_name).replace('FixImg',template_name).replace('MovImg',Mov_name).replace('MaskImg',Mask_name)
  call([job_string],shell=True)          
 output_image = Mov_name.replace('_Warped.nii.gz','_Warped2')
 if is_file_empty(output_name+'.nii.gz'):
  job_string = "greedy -d 3 -rf FixImg -rm MovImg OutImg.nii.gz -r "+output_name+'.nii.gz'
  job_string = job_string.replace('OutImg',output_image).replace('FixImg',template_name).replace('MovImg',Mov_name).replace('MaskImg',Mask_name)
  call([job_string],shell=True)

def Register_single_image_noMask_SecondPass(Mov_name,template_name):        
    output_name = Mov_name.replace('_Warped.nii.gz','_Greedy2')    
    file_name=os.path.basename(Mov_name)
    if is_file_empty(output_name+'.nii.gz'):        
        range2=int(file_name.split('range')[-1].split('_')[0])
        step=int(file_name.split('step')[-1].split('_')[0])
        TrueSlices=(range2/step)+1;
        if TrueSlices >= 16:
            job_string = "greedy -d 3 -o OutImg.nii.gz -i FixImg MovImg -sv -n 200x100x50 -e 0.25 -m NCC 2x2x2"
        else:
            job_string = "greedy -d 3 -o OutImg.nii.gz -i FixImg MovImg -sv -n 300x100 -e 0.25 -m NCC 2x2x2"
        job_string = job_string.replace('OutImg',output_name).replace('FixImg',template_name).replace('MovImg',Mov_name)
        call([job_string],shell=True)          
    output_image = Mov_name.replace('_Warped.nii.gz','_Warped2')
    if is_file_empty(output_image+'.nii.gz'):    
        job_string = "greedy -d 3 -rf FixImg -rm MovImg OutImg.nii.gz -r "+output_name+'.nii.gz'
        job_string = job_string.replace('OutImg',output_image).replace('FixImg',template_name).replace('MovImg',Mov_name)
        call([job_string],shell=True)
        
def Register_single_image_ThirdPass(Mov_name,template_name):        
    output_name = Mov_name.replace('_Warped2.nii.gz','_Greedy3')    
    if is_file_empty(output_name+'.nii.gz'):
        job_string = "greedy -d 3 -o OutImg.nii.gz -i FixImg MovImg -sv -n 200x100x50 -e 0.15 -m NCC 2x2x2"
        job_string = job_string.replace('OutImg',output_name).replace('FixImg',template_name).replace('MovImg',Mov_name)
        call([job_string],shell=True)          
    output_image = Mov_name.replace('_Warped2.nii.gz','_Warped3')
    if is_file_empty(output_image+'.nii.gz'):    
        job_string = "greedy -d 3 -rf FixImg -rm MovImg OutImg.nii.gz -r "+output_name+'.nii.gz'
        job_string = job_string.replace('OutImg',output_image).replace('FixImg',template_name).replace('MovImg',Mov_name)
        call([job_string],shell=True)
    
def Register_single_image(Mov_name,template_name,Mask_name):        
    output_name = Mov_name.replace('.tif','_Greedy')
    Affine_name = Mov_name.replace('.tif','_Greedy_affine.mat')
    if not os.path.exists(output_name+'_Greedy_affine.mat') and is_file_empty(output_name+'.nii.gz'):        
        output_name = Mov_name.replace('.tif','_Greedy') 
        Affine_name = Mov_name.replace('.tif','_Greedy_affine.mat')
        file_name=os.path.basename(Mov_name)
        range2=int(file_name.split('range')[-1].split('_')[0])
        step=int(file_name.split('step')[-1].split('_')[0])
        TrueSlices=(range2/step)+1;
        if TrueSlices >= 16:
            job_string = "greedy -d 3 -a -o Affine_name -i FixImg MovImg -gm MaskImg -n 200x80x40 -e 0.4 -ia-image-centers -m NCC 3x3x2"
        else:
            job_string = "greedy -d 3 -a -o Affine_name -i FixImg MovImg -gm MaskImg -n 300x100 -e 0.4 -ia-image-centers -m NCC 3x3x2"
        job_string = job_string.replace('Affine_name',Affine_name).replace('OutImg',output_name).replace('FixImg',template_name).replace('MovImg',Mov_name).replace('MaskImg',Mask_name)
        call([job_string],shell=True)  
        print(job_string)
        if TrueSlices >= 16:
            job_string = "greedy -d 3 -o OutImg.nii.gz -i FixImg MovImg -gm MaskImg -it Affine_name -n 200x80x40 -e 0.4 -m NCC 3x3x2"
        else:
            job_string = "greedy -d 3 -o OutImg.nii.gz -i FixImg MovImg -gm MaskImg -it Affine_name -n 300x100 -e 0.4 -m NCC 3x3x2"
        job_string = job_string.replace('Affine_name',Affine_name).replace('OutImg',output_name).replace('FixImg',template_name).replace('MovImg',Mov_name).replace('MaskImg',Mask_name)
        call([job_string],shell=True)  
        job_string = "greedy -d 3 -rf FixImg -rm MovImg MovImg_Warped.nii.gz -r OutImg.nii.gz Affine_name"
        job_string = job_string.replace('Affine_name',Affine_name).replace('OutImg',output_name).replace('FixImg',template_name).replace('MovImg',Mov_name).replace('MaskImg',Mask_name)
        call([job_string],shell=True)
        
def FindTemplate(tif_file_folder,number_of_frames_to_check=50):
    new_dir=os.path.join(tif_file_folder,'3Dreg/')
    tif_list_time=natsort.natsorted(glob.glob(new_dir+'*_time*.tif'))    
    for idx_nb in range(0,number_of_frames_to_check):
        file = tif_list_time[idx_nb]
        if idx_nb==0:
            temp=io.imread(file)
            dims=temp.shape
            concat_array=np.zeros((number_of_frames_to_check,)+dims)
            concat_array[idx_nb,:]=temp
        else:
            #temp=np.stack((temp,io.imread(file)))
            temp=io.imread(file)
            if dims==temp.shape:
             #print(temp2.shape)
             concat_array[idx_nb,:]=temp    
            else:
             concat_array[idx_nb,:]=np.transpose(temp,axes=(2,0,1))
    std_movie=np.diff(concat_array[0:number_of_frames_to_check,:],axis=0)    
    max_std=np.max(std_movie,axis=(1,2,3),keepdims=True)    
    idx_template=np.argmin(max_std)
    return(tif_list_time[idx_template])
        
def Register_single_image_forced(Mov_name,template_name,Mask_name):        
    output_name = Mov_name.replace('.tif','_Greedy').replace('3Dreg','3Dreg2')
    Affine_name = Mov_name.replace('.tif','_Greedy_affine.mat')
    file_name=os.path.basename(Mov_name)
    range2=int(file_name.split('range')[-1].split('_')[0])
    step=int(file_name.split('step')[-1].split('_')[0])
    TrueSlices=(range2/step)+1;
    if TrueSlices >= 16:
        job_string = "greedy -d 3 -a -o Affine_name -i FixImg MovImg -gm MaskImg -n 200x80x40 -e 0.4 -ia-image-centers -m NCC 3x3x2"
    else:
        job_string = "greedy -d 3 -a -o Affine_name -i FixImg MovImg -gm MaskImg -n 300x100 -e 0.4 -ia-image-centers -m NCC 3x3x2"    
    job_string = job_string.replace('Affine_name',Affine_name).replace('OutImg',output_name).replace('FixImg',template_name).replace('MovImg',Mov_name).replace('MaskImg',Mask_name)
    call([job_string],shell=True)  
    print(job_string)
    if TrueSlices >= 16:
        job_string = "greedy -d 3 -o OutImg.nii.gz -i FixImg MovImg -gm MaskImg -it Affine_name -n 200x80x40 -e 0.4 -m NCC 3x3x2"
    else:
        job_string = "greedy -d 3 -o OutImg.nii.gz -i FixImg MovImg -gm MaskImg -it Affine_name -n 300x100 -e 0.4 -m NCC 3x3x2"
    job_string = job_string.replace('Affine_name',Affine_name).replace('OutImg',output_name).replace('FixImg',template_name).replace('MovImg',Mov_name).replace('MaskImg',Mask_name)
    call([job_string],shell=True)  
    job_string = "greedy -d 3 -rf FixImg -rm MovImg MovImg_Warped.nii.gz -r OutImg.nii.gz Affine_name"
    job_string = job_string.replace('Affine_name',Affine_name).replace('OutImg',output_name).replace('FixImg',template_name).replace('MovImg',Mov_name).replace('MaskImg',Mask_name)
    call([job_string],shell=True)

tif_file_folder=sys.argv[1]
tif_file_folder=tif_file_folder.split('\r')[0]# removes the return to line
raw_string = r"{}".format(tif_file_folder)
#print(raw_string)
#Hardcoding this for now
#tif_file_folder=glob.glob(os.path.join('/faststorage/project/FUNCT_ENS/data/**/',tif_file_folder)+'/',recursive=True)[0]
#paths = [line for line in subprocess.check_output("find /faststorage/project/FUNCT_ENS/data/ -type d -iname '"+tif_file_folder+"'", shell=True).splitlines()]
tif_file_folder=os.path.normpath(tif_file_folder)
print(tif_file_folder)
img_seq_list=glob.glob(os.path.join(tif_file_folder,'3Dreg/*_Greedy.nii.gz'))
if not img_seq_list:
 job_string=r'find '+tif_file_folder+r' -type f -name "*.nii" -exec gzip {} -f \;'
 call([job_string],shell=True)
 img_seq_list=glob.glob(os.path.join(tif_file_folder,'3Dreg/*_Greedy.nii.gz'))

if not img_seq_list:
    img_seq_list=glob.glob(os.path.join(tif_file_folder,'3Dreg/*.tif'))
 
#You need to modify the next two lines to match where your template and masks are
template_name=os.path.join(tif_file_folder,'3Dreg/template.tif')
mask_name='/faststorage/project/FUNCT_ENS/TemplateFiles/Done/'+os.path.basename(tif_file_folder).split('_range')[0]+'_template.tif'
if not os.path.exists(mask_name):
 file_name=os.path.basename(img_seq_list[0])
 mask_name=file_name.split('_range')[0]+'_TEMPLATE.tif'
 date_name=mask_name.split('_RS_')[0]
 date_name='20'+date_name[-2:]+date_name[2:4]+date_name[0:2]
 mask_name=os.path.join(os.path.join(tif_file_folder),'RS_'+date_name+'_'+mask_name.split('_RS_')[1])

if not os.path.exists(template_name):
    temp_file=tifffile.imread(FindTemplate(tif_file_folder))
    tifffile.imwrite(template_name,temp_file.astype(np.uint16))
    
img_seq_list2=glob.glob(os.path.join(tif_file_folder,'3Dreg/*_Warped2.nii.gz'))

#First check if the files were warped once, or twice
if len(img_seq_list)>=1200 and len(img_seq_list2)<1200:
 print('need to do the second warp')
 for img_name in img_seq_list:
  if not os.path.exists(img_name.replace('_Greedy.nii.gz','_Warped2.nii.gz')):
   Mov_name = img_name.replace('_Greedy.nii.gz','.tif')
   job_string = "greedy -d 3 -rf FixImg -rm MovImg MovImg_Warped.nii.gz -r OutImg.nii.gz Affine_name"
   output_name = Mov_name.replace('.tif','_Greedy')
   Affine_name = Mov_name.replace('.tif','_Greedy_affine.mat')
   job_string = job_string.replace('Affine_name',Affine_name).replace('OutImg',output_name).replace('FixImg',template_name).replace('MovImg',Mov_name).replace('MaskImg',mask_name)
   call([job_string],shell=True)
   Register_single_image_SecondPass(img_name,template_name,mask_name)
elif glob.glob(tif_file_folder+'/3Dreg/*_Greedy.nii'):
 print('still some files not zipped')
 img_seq_list=glob.glob(tif_file_folder+'/3Dreg/*_Greedy.nii')
 job_string=r'find '+tif_file_folder+r' -type f -name "*.nii" -exec gzip {} -f \;'
 call([job_string],shell=True) 
 img_seq_list=glob.glob(tif_file_folder+'/3Dreg/*_Greedy.nii.gz')
 for img_name in img_seq_list:
  if not os.path.exists(img_name.replace('_Greedy.nii.gz','_Warped2.nii.gz')):
   Mov_name = img_name.replace('_Greedy.nii.gz','.tif')
   job_string = "greedy -d 3 -rf FixImg -rm MovImg MovImg_Warped.nii.gz -r OutImg.nii.gz Affine_name"
   output_name = Mov_name.replace('.tif','_Greedy')
   Affine_name = Mov_name.replace('.tif','_Greedy_affine.mat')
   job_string = job_string.replace('Affine_name',Affine_name).replace('OutImg',output_name).replace('FixImg',template_name).replace('MovImg',Mov_name).replace('MaskImg',mask_name)
   call([job_string],shell=True)
   Register_single_image_SecondPass(img_name,template_name,mask_name)
elif len(img_seq_list)<1200:
 print('need to do the first and second warp')
 tif_list=[x for x in glob.glob(os.path.join(tif_file_folder,'3Dreg/*.tif')) if not 'Warped' in x]
 for img_name in tif_list:
  Register_single_image(img_name,template_name,mask_name)
  Register_single_image_SecondPass(img_name.replace('.tif','_Warped.nii.gz'),template_name,mask_name)
else:
    print('Folder '+tif_file_folder+' has been warped twice')

#os.chdir(os.path.dirname(tif_file_folder))
img_seq_list=glob.glob(os.path.join(tif_file_folder,'3Dreg/*_Warped2.nii.gz'))
if os.path.exists(tif_file_folder+'/3Dreg/template.tif'):
    template_name=tif_file_folder+'/3Dreg/template.tif'
else:
    file_name=os.path.basename(tif_file_folder)
    mask_name=file_name.split('_range')[0]+'_TEMPLATE.tif'
    date_name=mask_name.split('_RS_')[0]
    date_name='20'+date_name[-2:]+date_name[2:4]+date_name[0:2]
    template_name=os.path.join(tif_file_folder,'RS_'+date_name+'_'+mask_name.split('_RS_')[1]) 
    

print(os.path.join(tif_file_folder,'3Dreg/*_Warped2.nii.gz')+' '+str(len(img_seq_list)))
#mask_name='/faststorage/project/FUNCT_ENS/TemplateFiles/Done/'+os.path.basename(tif_file_folder).split('_range')[0]+'_template.tif'
for img_name in img_seq_list:
 Register_single_image_ThirdPass(img_name,template_name)
 print(img_name)

MC_img_list=glob.glob(tif_file_folder+'/3Dreg/*'+os.path.basename(os.path.normpath(tif_file_folder))+'*_Warped3.nii.gz')    
#MC_img_list=[x for x in MC_img_list if not 'LongReg' in x]
print(tif_file_folder+' '+str(len(MC_img_list)))
#f = open(tif_file_folder+'/ListOfFailedFiles.txt','w')
#file_name=os.path.basename(os.path.normpath(tif_file_folder))
#if len(MC_img_list)==1200:
#  C1_name=MC_img_list[0] 
#  range2=int(file_name.split('range')[-1].split('_')[0])
#  step=int(file_name.split('step')[-1].split('_')[0])
#  TrueSlices=int((range2/step)+1);    
#  try:
#   base_img=nib.load(C1_name)
#  except:
#   Register_single_image_noMask_SecondPass(C1_name.replace('_Greedy2.nii.gz',''),template_name)
#   base_img=nib.load(C1_name)
#  base_img=np.squeeze(np.asarray(base_img.get_fdata(),dtype='uint16')).transpose()        
#  C1frames=np.zeros((int(len(MC_img_list)),TrueSlices,base_img.shape[1],base_img.shape[2]), dtype='uint16')
#  for img_nb,C2_name in enumerate(MC_img_list):    
#   img_nb=int( re.search('_power.+_(\d+)\.tif',C2_name).group(1)) 
#   try:
#    img_temp=nib.load(C2_name)
#    img_temp=img_temp.get_fdata()
#   except:
#    Register_single_image_noMask_SecondPass(C2_name.replace('_Greedy2.nii.gz',''),template_name)
#    img_temp=nib.load(C1_name)
#    img_temp=img_temp.get_fdata()    
#   img_temp=np.squeeze(np.asarray(img_temp,dtype='uint16')).transpose()
#   C1frames[img_nb,:,:,:]=img_temp 
#  tifffile.imwrite(tif_file_folder+'/'+file_name+'_4D2.tif',C1frames)
#  #nrrd.write(tif_file_folder+'/'+file_name+'_4D.nrrd',C1frames)   
#  print(tif_file_folder + 'is done')
# else:
#  test=[x.split('_Greedy2.nii.gz')[0] for x in MC_img_list]
#  test=set(test) ^ set(img_seq_list)
#  for img_name in test:
#   Register_single_image_noMask_SecondPass(img_name,template_name)
#   print(img_name)

#MC_img_list=[x for x in MC_img_list if not 'LongReg' in x]
print(tif_file_folder+' '+str(len(MC_img_list)))    
file_name=os.path.basename(os.path.normpath(tif_file_folder))
if len(MC_img_list)==1200 and not os.path.exists(tif_file_folder+'/'+file_name+'_4D2_MaxZ.tif'):
 C1_name=MC_img_list[0] 
 range2=int(file_name.split('range')[-1].split('_')[0])
 step=int(file_name.split('step')[-1].split('_')[0])
 TrueSlices=int((range2/step)+1);    
 try:
  base_img=nib.load(C1_name)
 except:
  Register_single_image_ThirdPass(C1_name.replace('_Warped3.nii.gz','_Warped2.nii.gz'),template_name)  
  base_img=nib.load(C1_name)
 base_img=np.squeeze(np.asarray(base_img.get_fdata(dtype='float16'),dtype='uint16')).transpose()        
 C1frames=np.zeros((int(len(MC_img_list)),TrueSlices,base_img.shape[1],base_img.shape[2]), dtype='uint16')
 for img_nb,C2_name in enumerate(MC_img_list):    
  img_nb=int( re.search('_power.+_time(\d+)\.tif.',C2_name).group(1)) 
  try:
   img_temp=nib.load(C2_name)
   img_temp=img_temp.get_fdata(dtype='float16')
  except:
   Register_single_image_ThirdPass(C1_name.replace('_Warped3.nii.gz','_Warped2.nii.gz'),template_name)  
   img_temp=nib.load(C1_name)
   img_temp=img_temp.get_fdata(dtype='float16')    
  img_temp=np.squeeze(np.asarray(img_temp,dtype='uint16')).transpose()
  C1frames[img_nb,:,:,:]=img_temp 
 #tifffile.imwrite(tif_file_folder+'/'+file_name+'_4D.tif',C1frames)
 tifffile.imwrite(tif_file_folder+'/'+file_name+'_4D2_MaxZ.tif',np.max(C1frames,axis=1))
 tifffile.imwrite(tif_file_folder+'/'+file_name+'_4D2_MeanT.tif',np.mean(C1frames,axis=0))
 print(tif_file_folder + 'is done')