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

os.environ["CAIMAN_TEMP"]="/faststorage/project/FUNCT_ENS/CaImAnTemp/"
os.environ["SLURM_SUBMIT_DIR"] = "/faststorage/project/FUNCT_ENS/CaImAnTemp/"
import caiman as cm
from caiman.source_extraction import cnmf
#from caiman.motion_correction import MotionCorrect
#from caiman.source_extraction.cnmf import params as params
import cv2
#from subprocess import call
opencv=True

try:
    cv2.setNumThreads(1)
except:
    pass

#%% start a cluster for parallel processing (if a cluster already exists it will be closed and a new session will be opened)
OutputFileAppend='_MIP'
n_processes=4
c, dview, n_processes = cm.cluster.setup_cluster( n_processes=n_processes, single_thread=False)

frate = 2                       # movie frame rate
decay_time = 1.6                 # length of a typical transient in seconds
# motion correction parameters
motion_correct = True    # flag for performing motion correction
pw_rigid = True         # flag for performing piecewise-rigid motion correction (otherwise just rigid)
gSig_filt = (10, 10)       # size of high pass spatial filtering, used in 1p data
max_shifts = (10, 10)      # maximum allowed rigid shift
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
#fnames=[os.path.normpath('/faststorage/project/FUNCT_ENS/Processed')]
fnames=[os.path.normpath(sys.argv[1])]
FourD_Files = glob.glob(os.path.join(fnames[0],'*_MaxZ.tif'))
for FourD_File in FourD_Files:
    if not os.path.exists(FourD_File.replace('.tif',OutputFileAppend+'.hdf5')):
        cm.stop_server(dview=dview)
        c, dview, n_processes = cm.cluster.setup_cluster( n_processes=n_processes, single_thread=False)
        # dataset dependent parameters
        print(FourD_File)
        opts = cnmf.params.CNMFParams(params_dict=mc_dict)
        fnames=[FourD_File]
        #if not os.path.isfile(fnames[0].replace('.tif','.hdf5')):
        mc = cm.motion_correction.MotionCorrect(fnames, dview=dview, **opts.get_group('motion'))
        mc.motion_correct(save_movie=True)
        fname_new = cm.save_memmap(mc.mmap_file, base_name='memmap_'+FourD_File, order='C',border_to_0=0, dview=dview) # exclude borders
        # load memory mappable file
        Yr, dims, T = cm.load_memmap(fname_new)
        #images = Yr.astype(np.uint16).T.reshape((T,) + dims, order='F')
        images = Yr.T.reshape((T,) + dims, order='F')
        # parameters for source extraction and deconvolution
        p = 1               # order of the autoregressive system
        K = 100            # upper bound on number of components per patch, in general None
        gSig = (4, 4)       # gaussian width of a 2D gaussian kernel, which approximates a neuron
        merge_thr = .7      # merging threshold, max correlation allowed
        rf = None             # half-size of the patches in pixels. e.g., if rf=40, patches are 80x80
        stride_cnmf = None    # amount of overlap between the patches in pixels
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
        min_corr = .6       # min peak value from correlation image
        min_pnr = 5        # min peak to noise ration from PNR image
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
                                        'border_pix': 5})                # number of pixels to not consider in the borders)
        
        
        cnm = cnmf.CNMF(n_processes, params=opts, k=K, gSig=gSig, merge_thresh=merge_thr, p=p,dview=dview,rf=rf,stride=stride_cnmf,only_init_patch=True)
        cnm.fit(images)
        cnm.save(FourD_File.replace('.tif',OutputFileAppend+'Temp.hdf5'))
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
        
        cnm.save(FourD_File.replace('.tif',OutputFileAppend+'.hdf5'))
        
        #%% RE-RUN seeded CNMF on accepted patches to refine and perform deconvolution 
        cnm2 = cnm.refit(images, dview=dview)
        cnm2.estimates.evaluate_components(images, cnm2.params, dview=dview)
        
        cnm2.save(FourD_File.replace('.tif',OutputFileAppend+'b.hdf5'))