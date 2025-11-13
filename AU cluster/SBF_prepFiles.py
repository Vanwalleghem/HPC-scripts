import sys
import os
import shutil
import glob
import os
import tifffile
import numpy as np
import time
import caiman as cm
from caiman.source_extraction import cnmf
from caiman.motion_correction import MotionCorrect
from caiman.source_extraction.cnmf import params as params
import cv2
from subprocess import call
opencv=True
import re
import gc

tif_folder=os.path.normpath(sys.argv[1])
Tif_4D_file_to_convert=glob.glob(os.path.join(tif_folder,'*.4D2.tif'))
Tif_4D_file_to_convert=Tif_4D_file_to_convert[0]
TifMem=np.memmap(Tif_4D_file_to_convert)
if TifMem.dtype not uint16:
  TifMem=TifMem.astype(uint16)
  TifMem.flush()


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

n_processes=6
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

if not is_file_empty(brain_file_name): #Need to convert tif stack into a giant 4D movie
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

del Y
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

mc = cm.motion_correction.MotionCorrect(brain_file_name, dview=dview, **opts.get_group('motion'))
mc.motion_correct(save_movie=True)
fname_new = cm.save_memmap(mc.mmap_file, base_name='memmap_', order='C',border_to_0=0, dview=dview) # exclude borders

if not glob.glob(os.path.join('/faststorage/project/FUNCT_ENS/CaImAnTemp/',os.path.basename(FourD_File[0]).replace('.tif','*.mmap'))):
 mc = cm.motion_correction.MotionCorrect(brain_file_name, dview=dview, **opts.get_group('motion'))
 try:
  mc.motion_correct(save_movie=True)
 except:
  time.sleep(10)
  if not glob.glob(os.path.join('/faststorage/project/FUNCT_ENS/CaImAnTemp/',os.path.basename(brain_file_name).replace('.tif','*.mmap'))):
   mc = cm.motion_correction.MotionCorrect(brain_file_name, dview=dview, **opts.get_group('motion'))

#if glob.glob(os.path.join('/faststorage/project/FUNCT_ENS/CaImAnTemp/',os.path.basename(brain_file_name).replace('.tif','*.mmap'))):
 #filename=glob.glob(os.path.join('/faststorage/project/FUNCT_ENS/CaImAnTemp/',os.path.basename(brain_file_name).replace('.tif','*.mmap')))
fname_new = cm.save_memmap(mc.mmap_file, base_name='memmap_', order='C',border_to_0=0, dview=dview) # exclude borders
#else:
 #mc.motion_correct(save_movie=True)

time.sleep(10)
Yr, dims, T = cm.load_memmap(fname_new)
images = np.reshape(Yr.T, [T] + list(dims), order='F') 
    #load frames in python format (T x X x Y)

# set parameters
rf = 25  # half-size of the patches in pixels. rf=25, patches are 50x50
stride = 10  # amount of overlap between the patches in pixels
K = 100  # number of neurons expected per patch
gSig = [2, 2, 1]  # expected half size of neurons
merge_thr = 0.8  # merging threshold, max correlation allowed
p = 1  # order of the autoregressive system
tsub = 1            # downsampling factor in time for initialization,
ssub = 1            # downsampling factor in space for initialization,
min_pnr = 2        # min peak to noise ration from PNR image
ssub_B = 5          # additional downsampling factor in space for background
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

min_SNR = 2            # adaptive way to set threshold on the transient size
r_values_min = 0.6    # threshold on space consistency (if you lower more components
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
cnm.save(brain_file_name.replace('.tif','_new.hdf5'))
cnm2 = cnm.refit(images, dview=dview)
cnm2.estimates.evaluate_components(images, cnm2.params, dview=dview)

print(' ***** ')
print(f"Number of total components: {len(cnm2.estimates.C)}")
print(f"Number of accepted components: {len(cnm2.estimates.idx_components)}")

cnm2.save(brain_file_name.replace('.tif','b_new.hdf5'))

cm.stop_server(dview=dview)