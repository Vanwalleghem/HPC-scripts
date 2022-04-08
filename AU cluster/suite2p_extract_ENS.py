import numpy as np
import sys
import os
from suite2p import run_s2p,default_ops
import shutil
import glob
fnames=[os.path.normpath(sys.argv[1])]

# set your options for running
data_path = os.path.dirname(fnames[0])
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
ops['smooth_sigma']=4
ops['high_pass']=30
ops['nchannels']=1
ops['spatial_taper']=5
ops['pre_smooth']=2
ops['max_iterations']=100
ops['inner_neuropil_radius']=1
ops['neuropil_extract']=0
ops['baseline']='prctile'
ops['nplanes'] = nplanes

print(data_path+'/suite2p_'+os.path.basename(fnames[0]))
#Check if suite2p has already run
#if not os.path.isdir(data_path+'/suite2p_'+os.path.basename(fnames[0])):
file = glob.glob(os.path.join(fnames[0],'*4D.tif'))        
db = {'look_one_level_down': False, # whether to look in ALL subfolders when searching for tiffs
      'data_path': fnames, # a list of folders with tiffs 
                                             # (or folder of folders with tiffs if look_one_level_down is True, or subfolders is not empty)         
      'fast_disk': os.environ["TMPDIR"], # string which specifies where the binary file will be stored (should be an SSD)
      'tiff_list': file, # list of tiffs in folder * data_path *!
      'save_folder': data_path+'/suite2p_'+os.path.basename(fnames[0])
    }
# run one experiment

opsEnd=run_s2p(ops=ops,db=db)