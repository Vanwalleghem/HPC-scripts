# -*- coding: utf-8 -*-
"""
Created on Fri May 30 16:42:52 2025

@author: au691573
"""

from subprocess import call
import glob
import os
import sys
import re

tif_file_folder=sys.argv[1]
tif_file_folder=os.path.normpath(tif_file_folder)
print(tif_file_folder)
if glob.glob(os.path.join(tif_file_folder,'3Dreg/','*_Jacobian3.nii.gz')):
 img_seq_list=glob.glob(os.path.join(tif_file_folder,'3Dreg/','*_Jacobian3.nii.gz'))
 Jacob_nb=3
else:
 img_seq_list=glob.glob(os.path.join(tif_file_folder,'3Dreg/','*_Jacobian2.nii.gz'))
 Jacob_nb=2

img_nb_list=[]
for name in img_seq_list:
 img_nb=int( re.search("power\\d+_(\\d+)_Jacobian",name).group(1))
 img_nb_list.append(img_nb)

nb_list=list(range(0,1199))
missing=[nb for nb in nb_list if nb not in img_nb_list]

warp_list=glob.glob(os.path.join(tif_file_folder,'3Dreg/','*CombinedWarp.nii.gz'))
missing_files=[]
for number in missing:
 temp=[x for x in warp_list if str(number) in x]
 missing_files.append(temp[0])

img_seq_list=glob.glob(os.path.join(tif_file_folder,'3Dreg/','*_Greedy.nii.gz'))
template_file=tif_file_folder+'/3Dreg/template.tif'
if Jacob_nb==3:
 for img_name in img_seq_list:     
 # if os.path.exists(img_name.replace('_Greedy.nii.gz','.tif_Greedy3.nii.gz')):
   output_name=img_name.replace('Greedy.nii.gz','CombinedWarp.nii.gz')
   job_string = "antsApplyTransforms -d 3 -o ["+output_name+",1] -t "+img_name.replace('_Greedy.nii.gz','.tif_Greedy3.nii.gz')+" -t "+img_name.replace('_Greedy.nii.gz','.tif_Greedy2.nii.gz')+" -t "+img_name+" -r "+template_file
   call([job_string],shell=True)
   Jacob_name = img_name.split('_Greedy.nii.gz')[0]+'_Jacobian3.nii.gz'
   #Compute the jacobian determinant of all the warps
   job_string = "CreateJacobianDeterminantImage 3 "+output_name+" "+Jacob_name+" 1 0"    
   call([job_string],shell=True)
elif Jacob_nb==2:
 for img_name in missing_files:  
    output_name = img_name
    Jacob_name = img_name.replace('CombinedWarp.nii.gz','_Jacobian2.nii.gz')
    #Compute the jacobian determinant of all the warps
    job_string = "CreateJacobianDeterminantImage 3 "+output_name+" "+Jacob_name+" 1 0"  
    call([job_string],shell=True)
    
    
