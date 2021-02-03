import sys
import os
import numpy as np
from scipy.io import savemat
import caiman as cm
from caiman.motion_correction import MotionCorrect
import caiman.source_extraction.cnmf as cnmf
import tifffile
fnames=[sys.argv[1]]	#name of the movie
fnames_orig=fnames
final_frate=int(os.environ["FPS"]) # frame rate in Hz
n_processes = 5 # if using the intel nodes
single_thread=True   
dview=None
gSig=[2,2] # expected half size of neurons, works for nuclear GCaMP
merge_thresh=0.8 # merging threshold, max correlation allowed
p=1 #order of the autoregressive system
downsample_factor=1 # use .2 or .1 if file is large and you want a quick answers
final_frate=final_frate*downsample_factor
init_method='greedy_roi'
spatial_factor=1
idx_xy=None
base_name=os.environ["TMPDIR"]+"/"+fnames[0].split('/')[-1][:-4]
print(fnames)
min_mov = cm.load(fnames[0], subindices=(0,10,100)).min()
mc = MotionCorrect(fnames[0],min_mov,max_shifts = [5,5],dview=dview,splits_rig = 1)    
mc.motion_correct_rigid(save_movie=True)
border_to_0 = np.ceil(np.max(mc.shifts_rig)).astype(np.int)
base_name=os.environ["TMPDIR"]+"/"+mc.fname_tot_rig.split('/')[-1][:-4]
fname_new = cm.save_memmap([mc.fname_tot_rig], base_name=base_name+'b', border_to_0=border_to_0)
Yr,dims,T=cm.load_memmap(fname_new)
Y=np.reshape(Yr,dims+(T,),order='F')
tifffile.imsave(fnames[0][:-4]+'_mean.tif',np.mean(Y,axis=2))
tifffile.imsave(fnames[0][:-4]+'_MC.tif',Y)

