# -*- coding: utf-8 -*-
"""
Created on Thu Dec 19 10:14:31 2024

@author: au691573
"""

import sys
import os
#import shutil
import glob
import logging
import natsort
import numpy as np

os.environ["CAIMAN_TEMP"]="/faststorage/project/FUNCT_ENS/CaImAnTemp/"

import caiman as cm
from caiman.source_extraction import cnmf
#from caiman.motion_correction import MotionCorrect
#from caiman.source_extraction.cnmf import params as params
import cv2
#from subprocess import call
import time
import datetime
from pathlib import Path
opencv=True

try:
    cv2.setNumThreads(0)
except:
    pass
    


logger = logging.getLogger("caiman")
logger.setLevel(logging.DEBUG)
# Set path to logfile
current_datetime = datetime.datetime.now().strftime("_%Y%m%d_%H%M%S")
log_filename = 'CaImAn1p' + current_datetime + '.log'
log_path = Path(cm.paths.get_tempdir()) / log_filename
# Done with path stuff
handler = logging.FileHandler(log_path)
log_format = logging.Formatter("%(relativeCreated)12d [%(filename)s:%(funcName)10s():%(lineno)s] [%(process)d] %(message)s")
handler.setFormatter(log_format)
logger.addHandler(handler)

n_processes=4
#%% start a cluster for parallel processing (if a cluster already exists it will be closed and a new session will be opened)

OutputFileAppend='_TifflistLow'

c, dview, n_processes = cm.cluster.setup_cluster(backend='multiprocessing', n_processes=n_processes, single_thread=False)

tif_file_folder=sys.argv[1]
tif_file_folder=tif_file_folder.split('\r')[0]# removes the return to line
raw_string = r"{}".format(tif_file_folder)
print(raw_string)
fnames=[os.path.normpath(tif_file_folder)]

#fnames=[os.path.normpath(sys.argv[1])]
print(fnames[0])
FourD_File = glob.glob(os.path.join(fnames[0],'*4D2.tif'))
print(FourD_File)
hdf5_name=FourD_File[0].replace('.tif','_movie.hdf5')
List_files=sorted(glob.glob(os.path.join(fnames[0],'3Dreg/*Warped3*.tif')))
if len(List_files)<1200:
 List_files=sorted(glob.glob(os.path.join(fnames[0],'3Dreg/*Warped2*.tif')))
List_files=[file_name for file_name in List_files if "template" not in file_name]
#List_number=[int(file_name.split('time')[1].split('.tif')[0]) for file_name in List_files if "template" not in file_name]
#List_number=[int(file_name.split('_power')[-1].split('_')[1].split('.tif')[0]) for file_name in List_files if "template" not in file_name]
print('number of warped files : ' + str(len(List_files)))
List_files=natsort.natsorted(List_files)

#Missing_tifs=sorted(set(range(List_number[0], List_number[-1])) - set(List_number))
#if Missing_tifs:
#    for file_nb in Missing_tifs:
#        file_name=glob.glob(os.path.join(fnames[0],'3Dreg/*'+str(file_nb)+'*Warped2.nii.gz'))[0]
#        if not file_name:
#            print('error, the warp for '+file_nb+' is missing')
#        else:
#            tif_volume=nib.load(file_name)
#            tif_volume=np.asarray(tif_volume.get_fdata(),dtype='uint16')
#            tifffile.imwrite(file_name.replace('.nii.gz','.tif'),tif_volume,bigtiff=True)  
if FourD_File:
 if glob.glob(FourD_File[0].replace('.tif',OutputFileAppend+'.hdf5')):
  print("Folder is done")
  exit()

print('Number of Tifs is: ' + str(len(List_files)))
if len(List_files)>1200:
    sys.exit("Too many tif files in: "+fnames[0])
hdf5_name=FourD_File[0].replace('.tif','_movie.hdf5')
if not glob.glob(hdf5_name):
    cm.load(List_files, is3D=True).save(hdf5_name)

fname2 = [hdf5_name]

# dataset dependent parameters
frate = 2                       # movie frame rate
decay_time = 1.6                 # length of a typical transient in seconds
# motion correction parameters
motion_correct = True    # flag for performing motion correction
pw_rigid = True         # flag for performing piecewise-rigid motion correction (otherwise just rigid)
gSig_filt = None #(4, 4, 2)       # size of high pass spatial filtering, used in 1p data
max_shifts = (5, 5, 2)      # maximum allowed rigid shift
strides = (24, 24, 3)       # start a new patch for pw-rigid motion correction every x pixels
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

#if not glob.glob(os.path.join('/faststorage/project/FUNCT_ENS/CaImAnTemp/',os.path.basename(FourD_File[0]).replace('.tif','*.mmap'))):
if True:
 mc = cm.motion_correction.MotionCorrect(fname2, dview=dview, **opts.get_group('motion'))
 try:
  print('1')
  mc.motion_correct(save_movie=True)
  fname_new2 = cm.save_memmap(mc.mmap_file, base_name='memmap_', order='C',border_to_0=0, dview=dview) # exclude borders
  Yr, dims, T = cm.load_memmap(fname_new2)
 except:
  time.sleep(10)
  print('2')
  #if not glob.glob(os.path.join('/faststorage/project/FUNCT_ENS/CaImAnTemp/',os.path.basename(FourD_File[0]).replace('.tif','*.mmap'))):
  mc = cm.motion_correction.MotionCorrect(fname2, dview=dview, **opts.get_group('motion'))
  mc.motion_correct(save_movie=True)   
  fname_new2 = cm.save_memmap(mc.mmap_file, base_name='memmap_', order='C',border_to_0=0, dview=dview) # exclude borders
  Yr, dims, T = cm.load_memmap(fname_new2)


#if glob.glob(os.path.join('/faststorage/project/FUNCT_ENS/CaImAnTemp/',os.path.basename(FourD_File[0]).replace('.tif','*.mmap'))):
# print('3')
# filename=glob.glob(os.path.join('/faststorage/project/FUNCT_ENS/CaImAnTemp/',os.path.basename(FourD_File[0]).replace('.tif','*.mmap'))) 
# Yr, dims, T = cm.load_memmap(filename[0])
#else:
# print('4')
# mc.motion_correct(save_movie=True) 
# fname_new2 = cm.save_memmap(mc.mmap_file, base_name='memmap_', order='C',border_to_0=0, dview=dview) # exclude borders
# time.sleep(10)
# Yr, dims, T = cm.load_memmap(fname_new2)
 
 

images = np.reshape(Yr.T, [T] + list(dims), order='F') 
    #load frames in python format (T x X x Y)
    

#%% restart cluster to clean up memory
cm.stop_server(dview=dview)
c, dview, n_processes = cm.cluster.setup_cluster(
    backend='multiprocessing', n_processes=None, single_thread=False)

# set parameters
rf = 25  # half-size of the patches in pixels. rf=25, patches are 50x50
stride = 10  # amount of overlap between the patches in pixels
K = 100  # number of neurons expected per patch
gSig = [3, 3, 2]  # expected half size of neurons
merge_thr = 0.9  # merging threshold, max correlation allowed
p = 1  # order of the autoregressive system
tsub = 2            # downsampling factor in time for initialization,
ssub = 1            # downsampling factor in space for initialization,
#min_pnr = 8        # min peak to noise ration from PNR image
min_pnr = 2        # min peak to noise ration from PNR image
ssub_B = 5          # additional downsampling factor in space for background
#min_corr=0.85
min_corr=0.7
ring_size_factor = 1.5  # radius of ring is gSiz*ring_size_factor
rval_thr = 0.6   # accept components with space correlation threshold or higher
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

cnm = cnmf.CNMF(n_processes, k=K, gSig=gSig, merge_thresh=merge_thr, p=p,dview=dview,rf=rf,stride=stride,only_init_patch=True,params=opts)
                
#cnm.params.set('spatial', {'se': np.ones((3,3,1), dtype=np.uint8)})
cnm = cnm.fit(images)

min_SNR = 1.5            # adaptive way to set threshold on the transient size
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
cnm.save(FourD_File[0].replace('.tif',OutputFileAppend+'.hdf5'))
cnm2 = cnm.refit(images, dview=dview)
cnm2.estimates.evaluate_components(images, cnm2.params, dview=dview)

print(' ***** ')
print(f"Number of total components: {len(cnm2.estimates.C)}")
print(f"Number of accepted components: {len(cnm2.estimates.idx_components)}")

cnm2.save(FourD_File[0].replace('.tif',OutputFileAppend+'b.hdf5'))

cm.stop_server(dview=dview)
os.remove(mc.mmap_file[0])