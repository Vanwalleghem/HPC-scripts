# -*- coding: utf-8 -*-
"""
Created on Wed Mar 25 10:04:51 2026

@author: au691573
"""
import glob
import os 
from datetime import date
from matplotlib import pyplot as plt
import numpy as np

# we need to set the current path to the directory
# containing the suite3d repository, this hack should
# do the trick
#os.chdir(os.path.dirname(os.path.abspath("")))

from suite3d.job import Job
from suite3d import io
from suite3d import plot_utils as plot

tif_file_folder='/faststorage/project/FUNCT_ENS/data/20200728/GV_20200727_fish5_ENS_4DPF_range100_step5_exposure23_power60/'
tifs = glob.glob(os.path.join(tif_file_folder,'3Dreg','*ped3.tif'))
file_name=os.path.basename(os.path.normpath(tif_file_folder))
range2=int(file_name.split('range')[-1].split('_')[0])
step=int(file_name.split('step')[-1].split('_')[0])
TrueSlices=int((range2/step)+1);    

planes=list(range(1,TrueSlices))


# Set the mandatory parameters
params = {
    # volume rate
    'fs': 2,
    
    # planes to analyze. 0 is typically the flyback, so we exclude it here
    'planes' : planes, 
    # number of planes recorded by scanimage, including the flyback
    'n_ch_tif' : 1,
    
    # Decay time of the Ca indicator in seconds. 1.3 for GCaMP6s. This example is for GCamP8m
    'tau' : 1.3,
    'lbm' : False, 
    'num_colors' : 1, # how many color channels were recorded by scanimage
    'functional_color_channel' : 0, # which color channel is the functional one
     # voxel size in z,y,x in microns
    'voxel_size_um' : (0.7, 0.7, range2),

    # number of files to use for the initial pass
    # usually, ~500 frames is a good rule of thumb
    # we will just use 200 here for speed
    'n_init_files' :  50,

    # 3D GPU registration - fast! 
    '3d_reg' : True,
    'gpu_reg' : False,
    
    # note : 3D CPU is not supported yet
    'subtract_crosstalk' : False, # turn off some lbm-only features
    'fuse_strips' : False, # turn off some lbm-only features

    
}


# Create the job
job = Job(r'/faststorage/project/FUNCT_ENS/data/','demo-std', tifs = tifs,
          params=params, create=True, overwrite=True, verbosity = 3)