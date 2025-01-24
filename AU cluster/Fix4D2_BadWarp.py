import glob
import os
import tifffile
import numpy as np
from subprocess import call
import nibabel as nib
import sys

def Warp_image_Twice(Mov_name):
    Warping_matrix = Mov_name.replace('.tif','_Greedy.nii.gz')
    Affine_name = Mov_name.replace('.tif','_Greedy_affine.mat')
    job_string = "greedy -d 3 -rf FixImg -rm MovImg MovImg_Warped.nii.gz -r OutImg Affine_name"
    job_string = job_string.replace('Affine_name',Affine_name).replace('OutImg',Warping_matrix).replace('FixImg',Mov_name).replace('MovImg',Mov_name)
    call(job_string,shell=True)    
    job_string = "greedy -d 3 -rf FixImg -rm MovImg_Warped.nii.gz MovImg_Warped2.nii.gz -r OutImg_Greedy2.nii.gz"
    job_string = job_string.replace('OutImg',Mov_name).replace('FixImg',Mov_name).replace('MovImg',Mov_name)
    call(job_string,shell=True)


def RegAndWarp_image_Twice(Mov_name,template_name,Mask_name):
    Warping_matrix = Mov_name.replace('.tif','_Greedy.nii.gz')
    Affine_name = Mov_name.replace('.tif','_Greedy_affine.mat')    
    print(Affine_name)
    job_string = "greedy -d 3 -a -o Affine_name -i FixImg MovImg -gm MaskImg -n 200x80x40 -e 0.4 -ia-image-centers -m NCC 3x3x2"
    job_string = job_string.replace('Affine_name',Affine_name).replace('OutImg',Warping_matrix).replace('FixImg',template_name).replace('MovImg',Mov_name).replace('MaskImg',Mask_name)
    call(job_string,shell=True)
    print(template_name)
    job_string = "greedy -d 3 -o OutImg.nii.gz -i FixImg MovImg -gm MaskImg -it Affine_name -n 200x80x40 -e 0.4 -m NCC 3x3x2"
    job_string = job_string.replace('Affine_name',Affine_name).replace('OutImg',Warping_matrix).replace('FixImg',template_name).replace('MovImg',Mov_name).replace('MaskImg',Mask_name)
    call(job_string,shell=True)
    job_string = "greedy -d 3 -rf FixImg -rm MovImg MovImg_Warped.nii.gz -r OutImg Affine_name"
    job_string = job_string.replace('Affine_name',Affine_name).replace('OutImg',Warping_matrix).replace('FixImg',Mov_name).replace('MovImg',Mov_name)
    call(job_string,shell=True)
    Warping_matrix2 = Mov_name.replace('.tif','_Greedy2.nii.gz')
    job_string = "greedy -d 3 -o OutImg -i FixImg MovImg_Warped.nii.gz -sv -n 200x100x50 -e 0.25 -m NCC 2x2x2"
    job_string = job_string.replace('OutImg',Warping_matrix2).replace('FixImg',template_name).replace('MovImg',Mov_name)
    call(job_string,shell=True) 
    job_string = "greedy -d 3 -rf FixImg -rm MovImg_Warped.nii.gz MovImg_Warped2.nii.gz -r OutImg_Greedy2.nii.gz"
    job_string = job_string.replace('OutImg',Mov_name).replace('FixImg',Mov_name).replace('MovImg',Mov_name)
    call(job_string,shell=True)
    return

#base_folder_to_search='/faststorage/project/FUNCT_ENS/data/'                       #May want to not make this hardcoded
base_folder_to_search=os.path.normpath(str(sys.argv[1]))
folder_list=glob.glob(base_folder_to_search+'/**/3Dreg/', recursive=True)
print('found '+str(len(folder_list))+' folders in '+base_folder_to_search)
for folder_tocheck in folder_list:
    Warped_files=glob.glob(folder_tocheck+'/*Warped2*')
    Size_Warped_files=[]
    for Warped_file in Warped_files:
        Size_Warped_files.append(os.path.getsize(Warped_file))
    Warped_files=np.asarray(Warped_files)
    Size_Warped_files=np.asarray(Size_Warped_files)
    Small_files=Warped_files[Size_Warped_files<0.5*Size_Warped_files.max()]    
    if Small_files.size>0:
        folder=os.path.dirname(os.path.dirname(folder_tocheck))
        file_name=os.path.basename(os.path.normpath(folder))
        tif_4D_name=os.path.join(folder,file_name+'_4D2.tif')
        memmap_volume = tifffile.memmap(tif_4D_name) #memmap the 4D2 tif file
        for file in Small_files:            
            mask_name='/faststorage/project/FUNCT_ENS/TemplateFiles/Done/'+os.path.basename(folder).split('_range')[0]+'_template.tif'
            RegAndWarp_image_Twice(file.split('_Warped2.nii.gz')[0],os.path.join(os.path.dirname(file),'template.tif'),mask_name)
            tif_volume=nib.load(file)
            tif_volume=np.asarray(tif_volume.get_fdata(),dtype='uint16')
            frame=file.split('.tif')[0].split('_')[-1]
            memmap_volume[int(frame),:,:,:]=tif_volume
            memmap_volume.flush()
        print(folder_tocheck+' is done')
    else:
        print('all good for this folder')