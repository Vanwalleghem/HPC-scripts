import glob
import os
import tifffile
import numpy as np
import matplotlib.pyplot as plt
from subprocess import call

def Warp_image_Twice(Mov_name):
    Warping_matrix = Mov_name.replace('.tif','_Greedy.nii.gz')
    Affine_name = Mov_name.replace('.tif','_Greedy_affine.mat')
    job_string = "greedy -d 3 -rf FixImg -rm MovImg MovImg_Warped.nii.gz -r OutImg Affine_name"
    job_string = job_string.replace('Affine_name',Affine_name).replace('OutImg',Warping_matrix).replace('FixImg',Mov_name).replace('MovImg',Mov_name)
    call(job_string,shell=True)
    Warping_matrix2 = Mov_name.replace('.tif','_Greedy2.nii.gz')
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
    
Txt_files=sorted(glob.glob("/faststorage/project/FUNCT_ENS/data/ToCheck/*.txt")) #May want to not make this hardcoded
base_folder_to_search='/faststorage/project/FUNCT_ENS/data/'                       #May want to not make this hardcoded
for txt_file in Txt_files:
    FramesToFix=[]
    with open(txt_file,'r') as the_file:
        while line := the_file.readline():
            FramesToFix.append(line.rstrip())
    FramesToFix.pop(0) #Removes the descriptive line
    tif_file_folder=os.path.basename(os.path.normpath(txt_file)).split('_Max')[0]    
    tif_file_folder=os.path.normpath(glob.glob(base_folder_to_search+'**/'+os.path.basename(os.path.normpath(txt_file)).split('_Max')[0]+'/', recursive=True)[0]) #looks for where the files are
    #The files are actually in the subfolder 3Dreg
    tif_file_folder=os.path.join(tif_file_folder,'/3Dreg/')
    for frame in FramesToFix:        
        frame_files=glob.glob(os.path.join(tif_file_folder,os.path.basename(os.path.normpath(txt_file)).split('_Max')[0]+'_'+frame+'*.tif'))
        Warp_image_Twice(frame_files[0])