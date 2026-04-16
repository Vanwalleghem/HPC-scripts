# -*- coding: utf-8 -*-
"""
Created on Tue Mar 31 17:10:59 2026

@author: snool
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Dec 19 10:14:31 2024

@author: au691573
"""

import sys
import os

os.environ["KMP_AFFINITY"] = "None"
os.environ["OMP_NUM_THREADS"] = "1"
#import shutil
import glob
import logging

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
    cv2.setNumThreads(1)
except:
    pass
    
tif_file_folder=sys.argv[1]
#tif_file_folder='/faststorage/project/FUNCT_ENS/NewENSDataDK/20231207/071223_RS_7DPF_GF_F1_HINDGUT_range145_step5_exposure10_power60'
tif_file_folder=tif_file_folder.split('\r')[0]# removes the return to line
#raw_string = r"{}".format(tif_file_folder)
#print(raw_string)
fnames=[os.path.normpath(tif_file_folder)]

#fnames=[os.path.normpath(sys.argv[1])]
print(fnames[0])
#Will need to get rid of the below
#FourD_File = glob.glob(os.path.join(fnames[0],'*4D2.tif'))

logger = logging.getLogger("caiman")
logger.setLevel(logging.DEBUG)
# Set path to logfile
current_datetime = datetime.datetime.now().strftime("_%Y%m%d_%H%M%S")
log_filename = 'CaImAn1p' + os.path.basename(fnames[0]) + '.log'
log_path = Path(cm.paths.get_tempdir()) / log_filename
# Done with path stuff
handler = logging.FileHandler(log_path)
log_format = logging.Formatter("%(relativeCreated)12d [%(filename)s:%(funcName)10s():%(lineno)s] [%(process)d] %(message)s")
handler.setFormatter(log_format)
logger.addHandler(handler)

n_processes=4
#%% start a cluster for parallel processing (if a cluster already exists it will be closed and a new session will be opened)

OutputFileAppend='_MIP'

c, dview, n_processes = cm.cluster.setup_cluster(n_processes=n_processes, single_thread=False)

#print(FourD_File)
#hdf5_name=FourD_File[0].replace('.tif','_movie.hdf5')
hdf5_name=fnames[0]

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

  

fname2 = [hdf5_name]

# dataset dependent parameters
frate = 2                       # movie frame rate
decay_time = 1.6                 # length of a typical transient in seconds
# motion correction parameters
motion_correct = True    # flag for performing motion correction
pw_rigid = True         # flag for performing piecewise-rigid motion correction (otherwise just rigid)
gSig_filt = (6, 6)       # size of high pass spatial filtering, used in 1p data
max_shifts = (5, 5)      # maximum allowed rigid shift
strides = (60, 60)       # start a new patch for pw-rigid motion correction every x pixels
overlaps = (24, 24)      # overlap between pathes (size of patch strides+overlaps)
max_deviation_rigid = 4  # maximum deviation allowed for patch with respect to rigid shifts
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
    'border_nan': border_nan
}

opts = cnmf.params.CNMFParams(params_dict=mc_dict)
file_to_save=os.path.join(tif_file_folder,'mem_file.txt')
print('Motion correcting: ' + fname2[0])
mc = cm.motion_correction.MotionCorrect(fname2, dview=dview, **opts.get_group('motion'))
mc.motion_correct(save_movie=True)
fname_new2 = cm.save_memmap(mc.mmap_file, base_name='memmap_'+os.path.basename(fnames[0]), order='C',border_to_0=0, dview=dview) # exclude borders
Yr, dims, T = cm.load_memmap(fname_new2)

print('dimensions :', dims, '. Number of frames :',T)
#if (T<1000):
# print('problem with dimensions')
# exit() 
 
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
 
#images = Yr.astype(np.uint16).T.reshape((T,) + dims, order='F')
images = Yr.T.reshape((T,) + dims, order='F')
# parameters for source extraction and deconvolution
p = 1               # order of the autoregressive system
K = 100            # upper bound on number of components per patch, in general None
gSig = (4, 4)       # gaussian width of a 2D gaussian kernel, which approximates a neuron
merge_thr = .7      # merging threshold, max correlation allowed
rf = 50             # half-size of the patches in pixels. e.g., if rf=40, patches are 80x80
stride_cnmf = 20    # amount of overlap between the patches in pixels
#                     (keep it at least large as gSiz, i.e 4 times the neuron size gSig)
tsub = 1            # downsampling factor in time for initialization,
#                     increase if you have memory problems
ssub = 1            # downsampling factor in space for initialization,
#                     increase if you have memory problems
#                     you can pass them here as boolean vectors
low_rank_background = None  # None leaves background of each patch intact,
#                     True performs global low-rank approximation if gnb>0
gnb = 0             # number of background components (rank) if positive,
#                     else exact ring model with following settings
#                         gnb= 0: Return background as b and W
#                         gnb=-1: Return full rank background B
#                         gnb<-1: Don't return background
nb_patch = 0        # number of background components (rank) per patch if gnb>0,
#                     else it is set automatically
min_corr = .7       # min peak value from correlation image
min_pnr = 8        # min peak to noise ration from PNR image
ssub_B = 3          # additional downsampling factor in space for background
ring_size_factor = 1.6  # radius of ring is gSiz*ring_size_factor

opts.change_params(params_dict={'method_init': 'corr_pnr',  # use this for 1 photon
								'K': K,
								'gSig': gSig,
								#'gSiz': (4 * gSig + 1, 4 * gSig + 1),
								'merge_thr': merge_thr,
								'p': p,
								'fr':2,
								'decay_time':1.4,
								'tsub': tsub,
								'ssub': ssub,
								'rf': rf,
								'stride': stride_cnmf,
								'only_init': True,    # set it to True to run CNMF-E
								'nb': gnb,
								'nb_patch': nb_patch,
								'method_deconvolution': 'oasis',       # could use 'cvxpy' alternatively
								'low_rank_background': low_rank_background,
								'update_background_components': True,  # sometimes setting to False improve the results
								'min_corr': min_corr,
								'min_pnr': min_pnr,
								'normalize_init': False,               # just leave as is
								'center_psf': True,                    # leave as is for 1 photon
								'ssub_B': ssub_B,
								'ring_size_factor': ring_size_factor,
								'del_duplicates': True,                # whether to remove duplicates from initialization
								'border_pix': 3})                # number of pixels to not consider in the borders)


cnm = cnmf.CNMF(n_processes, params=opts, k=K, gSig=gSig, merge_thresh=merge_thr, p=p,dview=dview,rf=rf,stride=stride_cnmf,only_init_patch=True)
cnm.fit(images)
cnm.save(hdf5_name.replace('.tif',OutputFileAppend+'Temp.hdf5'))
#%% COMPONENT EVALUATION
# the components are evaluated in two ways:
#   a) the shape of each component must be correlated with the data
#   b) a minimum peak SNR is required over the length of a transient
# Note that here we do not use the CNN based classifier, because it was trained on 2p not 1p data

min_SNR = 2            # adaptive way to set threshold on the transient size
r_values_min = 0.6    # threshold on space consistency (if you lower more components
#                        will be accepted, potentially with worst quality)
cnm.params.set('quality', {'min_SNR': min_SNR,
						   'rval_thr': r_values_min,
						   'use_cnn': False})
cnm.estimates.evaluate_components(images, cnm.params, dview=dview)

print(' ***** ')
print('Number of total components: ', len(cnm.estimates.C))
print('Number of accepted components: ', len(cnm.estimates.idx_components))

cnm.save(hdf5_name.replace('.tif',OutputFileAppend+'.hdf5'))

#%% RE-RUN seeded CNMF on accepted patches to refine and perform deconvolution 
cnm2 = cnm.refit(images, dview=dview)
cnm2.estimates.evaluate_components(images, cnm2.params, dview=dview)

cnm2.save(hdf5_name.replace('.tif',OutputFileAppend+'b.hdf5'))