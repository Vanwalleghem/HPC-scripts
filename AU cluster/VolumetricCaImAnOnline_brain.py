import sys
import os
import shutil
import glob
import os
import tifffile
import numpy as np
import caiman as cm
from caiman.source_extraction import cnmf
from caiman.motion_correction import MotionCorrect
from caiman.source_extraction.cnmf import params as params
import cv2
from subprocess import call
opencv=True
import re
import gc

try:
    cv2.setNumThreads(2)
except:
    pass
    
def is_file_empty(file_path):
 # Check if file exist and it is empty    
 if os.path.exists(file_path):
  if os.stat(file_path).st_size == 0:
   return True
  else:
   return False
 else:
  return True 

n_processes=4
#%% start a cluster for parallel processing (if a cluster already exists it will be closed and a new session will be opened)
if 'dview' in locals():
    cm.stop_server(dview=dview)

c, dview, n_processes = cm.cluster.setup_cluster(backend='single', n_processes=n_processes)

tif_folder=os.path.normpath(sys.argv[1])
tif_files=glob.glob(os.path.join(tif_folder,'3Dreg','*.tif'))
tif_files.sort()
print(tif_files[0])
FourD_File = glob.glob(os.path.join(tif_folder,'*4D2.tif'))
print(FourD_File)

if glob.glob(FourD_File[0].replace('.tif','_new_brain.hdf5')):
 print("Folder is done")
 exit()

brain_file_name=FourD_File[0].replace('4D2.tif','4D_brain.tif')

if is_file_empty(brain_file_name): #Need to convert tif stack into a giant 4D movie
#Y = cm.load_movie_chain(brain_file_name)
#Y.save(FourD_File[0].replace('4D2.tif','4D_brain.tif'))
 temp=tifffile.imread(tif_files[0])
 Y = tifffile.memmap(brain_file_name, dtype='uint16', shape=(1200,temp.shape[1],temp.shape[2],temp.shape[0]))
 print(Y.shape)
 for img_file in tif_files:
  temp=tifffile.imread(img_file)
  img_nb=int( re.search('_power.+_time(\d+)\.tif',img_file).group(1))
  Y[img_nb,:,:,:]=temp.transpose()
 Y.flush()

#Below is not needed since we made the file above  
#Y=cm.load(brain_file_name)
#if Y.shape[1]<100: #Ensures that the axis order matches the expectation of CaImAn (time, x,y,z)
# Y=np.moveaxis(Y, [3,1],[1,3])
# tifffile.imwrite(brain_file_name,Y)

try:
 del Y
except:
 pass

gc.collect()

# dataset dependent parameters
frate = 2                       # movie frame rate
decay_time = 1.6                 # length of a typical transient in seconds
# motion correction parameters
motion_correct = True    # flag for performing motion correction
pw_rigid = True         # flag for performing piecewise-rigid motion correction (otherwise just rigid)
gSig_filt = None #(3, 3, 2)       # size of high pass spatial filtering, used in 1p data
max_shifts = (5, 5, 2)      # maximum allowed rigid shift
strides = (24, 24, 6)       # start a new patch for pw-rigid motion correction every x pixels
overlaps = (12, 12, 2)      # overlap between pathes (size of patch strides+overlaps)
max_deviation_rigid = 3  # maximum deviation allowed for patch with respect to rigid shifts
border_nan = 'copy'      # replicate values along the boundaries
mc_dict = {    
    'fr': frate,
    'decay_time': decay_time,
    'pw_rigid': pw_rigid,
    'max_shifts': max_shifts,
    'gSig_filt': gSig_filt,
    'strides': strides,
    'overlaps': overlaps,
    'max_deviation_rigid': max_deviation_rigid,
    'border_nan': border_nan,
    'gnb': 0,
    'is3D': True
}

opts = cnmf.params.CNMFParams(params_dict=mc_dict)

# set parameters
rf = 25  # half-size of the patches in pixels. rf=25, patches are 50x50
stride = 10  # amount of overlap between the patches in pixels
K = 100  # number of neurons expected per patch
gSig = [1, 1, 1]  # expected half size of neurons
merge_thr = 0.8  # merging threshold, max correlation allowed
p = 1  # order of the autoregressive system
tsub = 2            # downsampling factor in time for initialization,
ssub = 1            # downsampling factor in space for initialization,
min_pnr = 1        # min peak to noise ration from PNR image
ssub_B = 5          # additional downsampling factor in space for background
ring_size_factor = 1.4  # radius of ring is gSiz*ring_size_factor
rval_thr = 0.5   # accept components with space correlation threshold or higher
expected_comps = 500                                                # maximum number of expected components used for memory pre-allocation (exaggerate here)

print('set')

opts = cnmf.params.CNMFParams(params_dict={
                                'fr': frate,
                                'fnames': brain_file_name,
                                'decay_time': decay_time,
                                'pw_rigid' : True,
                                'K': K,
                                'gSig': gSig,                                
                                'merge_thr': merge_thr,
                                'p': p,
                                'tsub': tsub,
                                'ssub': ssub,                                
                                'use_cnn':True,                                                 
                                'method_deconvolution': 'oasis',       # could use 'cvxpy' alternatively        
                                'update_background_components': True,                                
                                'min_pnr': min_pnr,
                                'normalize_init': False,               # just leave as is
                                'rval_thr': rval_thr,
                                'center_psf': True,                    # leave as is for 1 photon
                                'ssub_B': ssub_B,
                                'expected_comps': expected_comps,
                                'init_batch': 100,             # length of mini batch for initialization
                                'init_method': 'cnmf',         # initialization method for initial batch
                                'batch_update_suff_stat': True,# flag for updating sufficient statistics (used for updating shapes)
                                'only_init': False,            # whether to run only the initialization
                                'thresh_overlap': 0,           # space overlap threshold for screening new components
                                'ring_size_factor': ring_size_factor,
                                'del_duplicates': True,                # whether to remove duplicates from initialization
                                'is3D': True,
                                'border_pix': 0})                # The parameter border pix must be set to 0 for 3D data since border removal is not implemented)

opts.set('quality', {'min_cnn_thr': 0.05})

cnm = cnmf.online_cnmf.OnACID(params=opts)
cnm.fit_online();

print(' ***** ')
print(f"Number of total components: {len(cnm.estimates.C)}")
try:
 print(f"Number of accepted components: {len(cnm.estimates.idx_components)}")
except:
 pass

try:
    cnm.estimates.detrend_df_f(quantileMin=5, frames_window=200)
except:
    pass
    
cnm.save(brain_file_name.replace('.tif','_new.hdf5'))

cm.stop_server(dview=dview)