from subprocess import call
import glob
import os
import sys
import tifffile
from skimage import io
import numpy as np
import nibabel as nib
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
 output_name = Mov_name.replace('_Warp1.nii.gz','_orig2').replace('_orig.nii.gz','.tif_orig2').replace('.tif.tif','.tif')
 if is_file_empty(output_name+'.nii.gz'):   
  job_string = "greedy -d 3 -float -o OutImg.nii.gz -i FixImg MovImg -gm MaskImg -mm MaskImg -sv -n 300x150x50 -e 0.25 -m NCC 2x2x2"
  job_string = job_string.replace('OutImg',output_name).replace('FixImg',template_name).replace('MovImg',Mov_name).replace('MaskImg',Mask_name)
  call([job_string],shell=True)          
 output_image = Mov_name.replace('_Warp1.nii.gz','_Warp2')
 if is_file_empty(output_name+'.nii.gz'):
  job_string = "greedy -d 3 -rf FixImg -rm MovImg OutImg.nii.gz -r "+output_name+'.nii.gz'
  job_string = job_string.replace('OutImg',output_image).replace('FixImg',template_name).replace('MovImg',Mov_name).replace('MaskImg',Mask_name)
  call([job_string],shell=True)

def Register_single_image_noMask_SecondPass(Mov_name,template_name):        
    output_name = Mov_name.replace('_Warp1.nii.gz','_orig2')    
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
    output_image = Mov_name.replace('_Warp1.nii.gz','_Warp2')
    if is_file_empty(output_image+'.nii.gz'):    
        job_string = "greedy -d 3 -rf FixImg -rm MovImg OutImg.nii.gz -r "+output_name+'.nii.gz'
        job_string = job_string.replace('OutImg',output_image).replace('FixImg',template_name).replace('MovImg',Mov_name)
        call([job_string],shell=True)

def Register_single_image_ThirdPass(Mov_name,template_name):        
    output_name = Mov_name.replace('_Warp2.nii.gz','_orig3')    
    if is_file_empty(output_name+'.nii.gz'):
        job_string = "greedy -d 3 -o OutImg.nii.gz -i FixImg MovImg -sv -n 200x100x50 -e 0.15 -m NCC 2x2x2"
        job_string = job_string.replace('OutImg',output_name).replace('FixImg',template_name).replace('MovImg',Mov_name)
        call([job_string],shell=True)          
    output_image = Mov_name.replace('_Warp2.nii.gz','_Warp3')
    if is_file_empty(output_image+'.nii.gz'):    
        job_string = "greedy -d 3 -rf FixImg -rm MovImg OutImg.nii.gz -r "+output_name+'.nii.gz'
        job_string = job_string.replace('OutImg',output_image).replace('FixImg',template_name).replace('MovImg',Mov_name)
        call([job_string],shell=True)

def Register_single_image(Mov_name,template_name,Mask_name):        
    output_name = Mov_name.replace('.tif','_orig')
    Affine_name = Mov_name.replace('.tif','_orig_affine.mat')
    if not os.path.exists(output_name+'_orig_affine.mat') and is_file_empty(output_name+'.nii.gz'):        
        output_name = Mov_name.replace('.tif','_orig') 
        Affine_name = Mov_name.replace('.tif','_orig_affine.mat')
        file_name=os.path.basename(Mov_name)
        range2=int(file_name.split('range')[-1].split('_')[0])
        step=int(file_name.split('step')[-1].split('_')[0])
        TrueSlices=(range2/step)+1;
        if TrueSlices >= 16:
            job_string = "greedy -d 3 -a -o Affine_name -i FixImg MovImg -n 200x100x50 -e 0.5 -m NCC 3x3x2"
        else:
            job_string = "greedy -d 3 -a -o Affine_name -i FixImg MovImg -n 200x100x50 -e 0.5 -m NCC 3x3x2"
        job_string = job_string.replace('Affine_name',Affine_name).replace('OutImg',output_name).replace('FixImg',template_name).replace('MovImg',Mov_name)
        call([job_string],shell=True)  
        print(job_string)
        #if TrueSlices >= 16:
        #    job_string = "greedy -d 3 -o OutImg.nii.gz -i FixImg MovImg -gm MaskImg -it Affine_name -sv -n 300x150x80 -e 0.5  -m NCC 3x3x2"
        #else:
        job_string = "greedy -d 3 -s 1.8vox 1vox -o OutImg.nii.gz -i FixImg MovImg -gm MaskImg -mm MaskImg -it Affine_name -sv -n 300x150x80 -e 0.5 -m NCC 3x3x2"
        job_string = job_string.replace('Affine_name',Affine_name).replace('OutImg',output_name).replace('FixImg',template_name).replace('MovImg',Mov_name).replace('MaskImg',Mask_name)
        call([job_string],shell=True)  
        job_string = "greedy -d 3 -rf FixImg -rm MovImg MovImg_Warp1.nii.gz -r OutImg.nii.gz Affine_name"
        job_string = job_string.replace('Affine_name',Affine_name).replace('OutImg',output_name).replace('FixImg',template_name).replace('MovImg',Mov_name).replace('MaskImg',Mask_name)
        call([job_string],shell=True)

def FindTemplate(tif_file_folder,number_of_frames_to_check=50):
    new_dir=os.path.join(tif_file_folder,'3Dreg/')
    tif_list_time=natsort.natsorted(glob.glob(new_dir+'*_time*.tif'))    
    tif_list_time=[x for x in tif_list_time if 'arped' not in x]
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
    output_name = Mov_name.replace('.tif','_orig').replace('3Dreg','3Dreg2')
    Affine_name = Mov_name.replace('.tif','_orig_affine.mat')
    file_name=os.path.basename(Mov_name)
    range2=int(file_name.split('range')[-1].split('_')[0])
    step=int(file_name.split('step')[-1].split('_')[0])
    TrueSlices=(range2/step)+1;
    if TrueSlices >= 16:
        job_string = "greedy -d 3 -a -o Affine_name -i FixImg MovImg -gm MaskImg -n 200x80x40 -e 0.5 -ia-image-centers -m NCC 3x3x2"
    else:
        job_string = "greedy -d 3 -a -o Affine_name -i FixImg MovImg -gm MaskImg -n 300x100 -e 0.5 -ia-image-centers -m NCC 3x3x2"    
    job_string = job_string.replace('Affine_name',Affine_name).replace('OutImg',output_name).replace('FixImg',template_name).replace('MovImg',Mov_name).replace('MaskImg',Mask_name)
    call([job_string],shell=True)  
    print(job_string)
    if TrueSlices >= 16:
        job_string = "greedy -d 3 -o OutImg.nii.gz -i FixImg MovImg -gm MaskImg -it Affine_name -n 200x80x40 -e 0.5 -m NCC 3x3x2"
    else:
        job_string = "greedy -d 3 -o OutImg.nii.gz -i FixImg MovImg -gm MaskImg -it Affine_name -n 300x100 -e 0.5 -m NCC 3x3x2"
    job_string = job_string.replace('Affine_name',Affine_name).replace('OutImg',output_name).replace('FixImg',template_name).replace('MovImg',Mov_name).replace('MaskImg',Mask_name)
    call([job_string],shell=True)  
    job_string = "greedy -d 3 -rf FixImg -rm MovImg MovImg_Warp1.nii.gz -r OutImg.nii.gz Affine_name"
    job_string = job_string.replace('Affine_name',Affine_name).replace('OutImg',output_name).replace('FixImg',template_name).replace('MovImg',Mov_name).replace('MaskImg',Mask_name)
    call([job_string],shell=True)

#tif_file_folder='/faststorage/project/FUNCT_ENS/NewENSDataDK/20231204/041223_RS_4DPF_GF_F1_HINDGUT_range130_step5_exposure11_power60/'
tif_file_folder=sys.argv[1]
tif_file_folder=tif_file_folder.split('\r')[0]# removes the return to line
raw_string = r"{}".format(tif_file_folder)
tif_file_folder=os.path.normpath(tif_file_folder.split('3Dreg')[0])
print(tif_file_folder)

OutputFileAppendWarp=['Warp1','Warp2','Warp3']

img_seq_list=glob.glob(os.path.join(tif_file_folder,'3Dreg','*'+OutputFileAppendWarp[0]+'.nii.gz'))
if not img_seq_list:
 job_string=r'find '+tif_file_folder+r' -type f -name "*.nii" -exec gzip {} -f \;'
 call([job_string],shell=True)
 img_seq_list=glob.glob(os.path.join(tif_file_folder,'3Dreg/*_orig.nii.gz'))

if len(img_seq_list)<1200:
  warp_1=False
  img_seq_list=glob.glob(os.path.join(tif_file_folder,'3Dreg/*.tif'))
  img_seq_list=[x for x in img_seq_list if 'Warped' not in x]
  img_seq_list=[x for x in img_seq_list if 'template' not in x]
else:
  warp_1=True

#You need to modify the next two lines to match where your template and masks are
template_name=os.path.join(tif_file_folder,'3Dreg/Newtemplate.tif')
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

img_seq_list2=glob.glob(os.path.join(tif_file_folder,'3Dreg','*'+OutputFileAppendWarp[1]+'.nii.gz'))

#First check if the files were warped once, or twice
if len(img_seq_list)==1200 and len(img_seq_list2)<1200 and warp_1:
 print('need to do the second warp')
 for img_name in img_seq_list:
  if not os.path.exists(img_name.replace(OutputFileAppendWarp[0]+'.nii.gz',OutputFileAppendWarp[1]+'.nii.gz')):
   Mov_name = img_name.replace(OutputFileAppendWarp[0]+'.nii.gz','')
   #job_string = "greedy -d 3 -rf FixImg -rm MovImg MovImg_Warp1.nii.gz -r OutImg.nii.gz Affine_name"
   #output_name = Mov_name.replace('.tif',OutputFileAppendWarp[1]+'.nii.gz')
   #Affine_name = Mov_name.replace('.tif','_orig_affine.mat')
   #job_string = job_string.replace('Affine_name',Affine_name).replace('OutImg',output_name).replace('FixImg',template_name).replace('MovImg',Mov_name).replace('MaskImg',mask_name)
   #call([job_string],shell=True)
   Register_single_image_SecondPass(img_name,template_name,mask_name)
elif not warp_1:
 print('need to do the first and second warp')
 tif_list=[x for x in glob.glob(os.path.join(tif_file_folder,'3Dreg/*.tif')) if 'Warped' not in x]
 tif_list=[x for x in tif_list if 'template' not in x]
 for img_name in tif_list:
  Register_single_image(img_name,template_name,mask_name)
  Register_single_image_SecondPass(img_name.replace('.tif','_Warp1.nii.gz'),template_name,mask_name)
else:
    print('Folder '+tif_file_folder+' has been warped twice')

print(os.path.join(tif_file_folder,'3Dreg/*_Warp2.nii.gz')+' '+str(len(img_seq_list)))
#mask_name='/faststorage/project/FUNCT_ENS/TemplateFiles/Done/'+os.path.basename(tif_file_folder).split('_range')[0]+'_template.tif'
img_seq_list2=glob.glob(os.path.join(tif_file_folder,'3Dreg','*'+OutputFileAppendWarp[1]+'.nii.gz'))
if len(img_seq_list2)==1200:
 for img_name in img_seq_list2:
  Register_single_image_ThirdPass(img_name,template_name)


Warped_files=glob.glob(tif_file_folder+'/3Dreg/*'+os.path.basename(os.path.normpath(tif_file_folder))+'*_Warp3.nii.gz')    
#MC_img_list=[x for x in MC_img_list if not 'LongReg' in x]
print(tif_file_folder+' '+str(len(Warped_files)))

if not os.path.isfile(Warped_files[0].replace('.nii.gz','.tif')):
    for file_Warp1 in Warped_files:
        base_img=nib.load(file_Warp1)
        base_img=np.squeeze(np.asarray(base_img.get_fdata(),dtype='uint16'))
        tifffile.imwrite(file_Warp1.replace('.nii.gz','.tif'),base_img,bigtiff=True)

print('finished processing') 
exit('done')