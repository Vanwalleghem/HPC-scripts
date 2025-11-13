import sys
import os
import shutil
import glob
import logging
import os
import tifffile
import numpy as np
import caiman as cm
from caiman.source_extraction import cnmf
from caiman.motion_correction import MotionCorrect
from caiman.source_extraction.cnmf import params as params
import cv2
from subprocess import call
import time
opencv=True

try:
    cv2.setNumThreads(0)
except:
    pass

n_processes=4
#%% start a cluster for parallel processing (if a cluster already exists it will be closed and a new session will be opened) 
if 'dview' in locals():
    cm.stop_server(dview=dview)
c, dview, n_processes = cm.cluster.setup_cluster(backend='local', n_processes=n_processes, single_thread=False)

fnames=[os.path.normpath(sys.argv[1])]
print(fnames[0])
if not os.path.isdir(os.path.join(fnames[0],'CaImAnvolumes')):
  os.mkdir(os.path.join(fnames[0],'CaImAnvolumes'))
  tif_file_folder=os.path.join(fnames[0],'3Dreg/')
  Warped_files=glob.glob(tif_file_folder+'*Warped2*')
  Warped_files.sort()
  for Warped_file in Warped_files:
    tif_volume=nib.load(Warped_file)


if glob.glob(FourD_File[0].replace('.tif','_optCaImAn.hdf5')):
 print("Folder is done")
 exit()

# dataset dependent parameters
frate = 2                       # movie frame rate
decay_time = 1.6                 # length of a typical transient in seconds
# motion correction parameters
motion_correct = True    # flag for performing motion correction
pw_rigid = True         # flag for performing piecewise-rigid motion correction (otherwise just rigid)
gSig_filt = None #(4, 4, 2)       # size of high pass spatial filtering, used in 1p data
max_shifts = (5, 5, 2)      # maximum allowed rigid shift
strides = (24, 24, 4)       # start a new patch for pw-rigid motion correction every x pixels
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
    'shifts_opencv':True,
    'nonneg_movie':True,
    'is3D': True
}

opts = cnmf.params.CNMFParams(params_dict=mc_dict)

if not glob.glob(os.path.join('/faststorage/project/FUNCT_ENS/CaImAnTemp/',os.path.basename(FourD_File[0]).replace('.tif','*.mmap'))):
 mc = cm.motion_correction.MotionCorrect(FourD_File[0], dview=dview, **opts.get_group('motion'))
 try:
  print('1')
  mc.motion_correct(save_movie=True)
  fname_new2 = cm.save_memmap(mc.mmap_file, base_name='memmap_', order='C',border_to_0=0, dview=dview) # exclude borders
  Yr, dims, T = cm.load_memmap(fname_new2)
 except:
  time.sleep(10)
  print('2')
  if not glob.glob(os.path.join('/faststorage/project/FUNCT_ENS/CaImAnTemp/',os.path.basename(FourD_File[0]).replace('.tif','*.mmap'))):
   mc = cm.motion_correction.MotionCorrect(FourD_File[0], dview=dview, **opts.get_group('motion'))
   mc.motion_correct(save_movie=True)   
   fname_new2 = cm.save_memmap(mc.mmap_file, base_name='memmap_', order='C',border_to_0=0, dview=dview) # exclude borders
   Yr, dims, T = cm.load_memmap(fname_new2)


if glob.glob(os.path.join('/faststorage/project/FUNCT_ENS/CaImAnTemp/',os.path.basename(FourD_File[0]).replace('.tif','*.mmap'))):
 print('3')
 filename=glob.glob(os.path.join('/faststorage/project/FUNCT_ENS/CaImAnTemp/',os.path.basename(FourD_File[0]).replace('.tif','*.mmap'))) 
 Yr, dims, T = cm.load_memmap(filename[0])
else:
 print('4')
 mc.motion_correct(save_movie=True) 
 fname_new2 = cm.save_memmap(mc.mmap_file, base_name='memmap_', order='C',border_to_0=0, dview=dview) # exclude borders
 time.sleep(10)
 Yr, dims, T = cm.load_memmap(fname_new2)
 
 

images = np.reshape(Yr.T, [T] + list(dims), order='C') 
    #load frames in python format (T x X x Y)

# set parameters
rf = 25  # half-size of the patches in pixels. rf=25, patches are 50x50
stride = 10  # amount of overlap between the patches in pixels
K = 100  # number of neurons expected per patch
gSig = [4, 4, 2]  # expected half size of neurons
merge_thr = 0.95  # merging threshold, max correlation allowed
p = 1  # order of the autoregressive system
tsub = 2            # downsampling factor in time for initialization,
ssub = 1            # downsampling factor in space for initialization,
min_pnr = 10        # min peak to noise ration from PNR image
ssub_B = 5          # additional downsampling factor in space for background
min_corr=0.85
ring_size_factor = 1.4  # radius of ring is gSiz*ring_size_factor
rval_thr = 0.7   # accept components with space correlation threshold or higher
print('set')

opts = cnmf.params.CNMFParams(params_dict={
                                'K': K,
                                'gSig': gSig,                                
                                'merge_thr': merge_thr,
                                'p': p,
                                'tsub': tsub,
                                'ssub': ssub,                                
                                'use_cnn':True,                                
                                'only_init': True,    # set it to True to run CNMF-E                                                                
                                'method_deconvolution': 'oasis',       # could use 'cvxpy' alternatively        
                                'update_background_components': True,                                
                                'min_pnr': min_pnr,
                                'min_corr': min_corr,
                                'normalize_init': False,               # just leave as is
                                'rval_thr': rval_thr,
                                'center_psf': True,                    # leave as is for 1 photon
                                'ssub_B': 3,
                                'ring_size_factor': ring_size_factor,
                                'del_duplicates': True,                # whether to remove duplicates from initialization
                                'border_pix': 0})                # The parameter border pix must be set to 0 for 3D data since border removal is not implemented)

cnm = cnmf.CNMF(n_processes, k=K, gSig=gSig, merge_thresh=merge_thr, p=p,dview=dview,rf=rf,stride=stride,only_init_patch=True)
                
#cnm.params.set('spatial', {'se': np.ones((3,3,1), dtype=np.uint8)})
cnm = cnm.fit(images)

min_SNR = 4            # adaptive way to set threshold on the transient size
r_values_min = 0.5    # threshold on space consistency (if you lower more components
#                        will be accepted, potentially with worst quality)
cnm.params.set('quality', {'min_SNR': min_SNR,'rval_thr': r_values_min,'use_cnn': False})
cnm.estimates.evaluate_components(images, cnm.params, dview=dview)

print(' ***** ')
print(f"Number of total components: {len(cnm.estimates.C)}")
print(f"Number of accepted components: {len(cnm.estimates.idx_components)}")

try:
    cnm.estimates.detrend_df_f(quantileMin=5, frames_window=200)
except:
    pass
cnm.save(FourD_File[0].replace('.tif','_optCaImAn.hdf5'))
cnm2 = cnm.refit(images, dview=dview)
cnm2.estimates.evaluate_components(images, cnm2.params, dview=dview)

print(' ***** ')
print(f"Number of total components: {len(cnm2.estimates.C)}")
print(f"Number of accepted components: {len(cnm2.estimates.idx_components)}")

cnm2.save(FourD_File[0].replace('.tif','_optCaImAn.hdf5'))

cm.stop_server(dview=dview)