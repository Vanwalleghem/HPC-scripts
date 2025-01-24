# -*- coding: utf-8 -*-
"""
Created on Wed Jan  8 10:06:54 2025

@author: au691573
"""

import numpy as np
import sys
import os
from suite2p import run_s2p,default_ops
import glob
import tifffile
import nibabel as nib

fnames=[os.path.normpath(sys.argv[1])]

# set your options for running
data_path = os.path.normpath(fnames[0])
range2=int(fnames[0].split('range')[-1].split('_')[0])
step=int(fnames[0].split('step')[-1].split('_')[0])
nplanes=int((range2/step)+1);


ops=default_ops()
ops['fs']=2
ops['tau']=1.6
ops['save_mat']=1
ops['1Preg']=True
ops['denoise']=True
ops['diameter']=[3,4,5]
ops['threshold_scaling']=0.5
ops['max_iterations']=100
ops['smooth_sigma']=8
ops['high_pass']=30
ops['nchannels']=1
ops['block_size']=[64,64]
ops['spatial_taper']=10
ops['spikedetect']=False
ops['pre_smooth']=2
ops['max_iterations']=100
ops['inner_neuropil_radius']=1
ops['neuropil_extract']=0
ops['baseline']='prctile'
ops['nplanes'] = nplanes

#file = glob.glob(os.path.join(fnames[0],'*4D2.tif'))
Warped_files=glob.glob(os.path.join(fnames[0],'3Dreg/*Warped2.nii.gz'))
print(Warped_files[0])

db = {'look_one_level_down': False, # whether to look in ALL subfolders when searching for tiffs      
      'fast_disk': os.environ["TMPDIR"], # string which specifies where the binary file will be stored (should be an SSD)
      'save_folder': os.path.join(data_path,'suite2p_'+ os.path.basename(os.path.normpath(fnames[0])))
     }

if not os.path.isfile(Warped_files[0].replace('.nii.gz','.tif')):
    for file_warped in Warped_files:
        base_img=nib.load(file_warped)
        base_img=np.squeeze(np.asarray(base_img.get_fdata(),dtype='uint16'))
        tifffile.imwrite(file_warped.replace('.nii.gz','.tif'),base_img,bigtiff=True)

db['data_path']=os.path.join(data_path,'3Dreg/')
db['tiff_list']=sorted(glob.glob(os.path.join(fnames[0],'3Dreg/*Warped2.tif')))
opsEnd=run_s2p(ops=ops,db=db)
  

print('error in the tif_file ') 