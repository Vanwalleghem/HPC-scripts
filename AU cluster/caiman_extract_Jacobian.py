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
import tifffile
from subprocess import call


try:
    cv2.setNumThreads(0)
except:
    pass



tif_folder=os.path.normpath(sys.argv[1])
FourD_File = glob.glob(os.path.join(tif_folder,'*_3DJacob2.tif'))
FourD_TifFile = glob.glob(os.path.join(tif_folder,'*4D2.tif'))
print(FourD_File)
#Y=tifffile.imread(FourD_File[0])
#dims=Y.shape
#Only load the metadata to get the dimensions of the image
tif_info=tifffile.TiffFile(FourD_File[0])
dims=tif_info.series[0].shape

#%% start a cluster for parallel processing (if a cluster already exists it will be closed and a new session will be opened)
if 'dview' in locals():
    cm.stop_server(dview=dview)
    
c, dview, n_processes = cm.cluster.setup_cluster(backend='local', n_processes=None, single_thread=False)

for slice_nb in range(0,dims[1]):
    fnames=[os.path.join(tif_folder,'temp.tif')]
    caiman_filename=os.path.basename(FourD_TifFile[0]).replace('.tif','_slice'+str(slice_nb+1)+'.tif').replace('.tif','b.hdf5')
    caiman_filename=os.path.abspath(os.path.join(tif_folder,'../../CaImAn2/',caiman_filename))
    #if not os.path.isfile(fnames[0].replace('.tif','.hdf5')):
    SlicedImg=tifffile.imread(FourD_File[0],key=range(slice_nb,len(tif_info.pages),dims[1]))
    tifffile.imwrite(fnames[0],SlicedImg)
    fname_new = cm.save_memmap(fnames, base_name='memmap_'+str(slice_nb), order='C',border_to_0=5)
    # load memory mappable file
    Yr, dims, T = cm.load_memmap(fname_new)
    images = Yr.T.reshape((T,) + dims, order='F')
    cnm_seed=cnmf.cnmf.load_CNMF(caiman_filename)
    opts = params.CNMFParams()
    # parameters for source extraction and deconvolution
    p = 1               # order of the autoregressive system
    K = None            # upper bound on number of components per patch, in general None
    gSig = (3, 3)       # gaussian width of a 2D gaussian kernel, which approximates a neuron
    gSiz = (10, 10)     # average diameter of a neuron, in general 4*gSig+1
    Ain = None          # possibility to seed with predetermined binary masks
    merge_thr = .8      # merging threshold, max correlation allowed
    rf = None                   # half-size of the patches in pixels. Should be `None` when seeded CNMF is used.             
    #                     (keep it at least large as gSiz, i.e 4 times the neuron size gSig)
    tsub = 1            # downsampling factor in time for initialization,
    #                     increase if you have memory problems
    ssub = 1            # downsampling factor in space for initialization,
    #                     increase if you have memory problems
    #                     you can pass them here as boolean vectors
    low_rank_background = None  # None leaves background of each patch intact,
    #                     True performs global low-rank approximation if gnb>0
    gnb = 1             # number of background components (rank) if positive,
    #                     else exact ring model with following settings
    #                         gnb= 0: Return background as b and W
    #                         gnb=-1: Return full rank background B
    #                         gnb<-1: Don't return background
    nb_patch = 0        # number of background components (rank) per patch if gnb>0,
    #                     else it is set automatically
    min_corr = .8       # min peak value from correlation image
    min_pnr = 2        # min peak to noise ration from PNR image
    ssub_B = 3          # additional downsampling factor in space for background
    ring_size_factor = 1.5  # radius of ring is gSiz*ring_size_factor

    opts.change_params(params_dict={'K': K,
                                    'gSig': gSig,
                                    'gSiz': gSiz,
                                    'merge_thr': merge_thr,
                                    'p': p,
                                    'tsub': tsub,
                                    'ssub': ssub,
                                    'rf': rf,                                    
                                    'only_init': False,    # has to be `False` when seeded CNMF is used
                                    'nb': gnb,                                    
                                    'method_deconvolution': 'oasis',       # could use 'cvxpy' alternatively
                                    'low_rank_background': low_rank_background,
                                    'update_background_components': True,  # sometimes setting to False improve the results
                                    'min_corr': min_corr,
                                    'min_pnr': min_pnr,                                    
                                    'border_pix': 10})                # number of pixels to not consider in the borders)


    cnm = cnmf.CNMF(n_processes=n_processes, dview=dview, Ain=cnm_seed.estimates.A, params=opts)
    cnm.fit(images)

    #%% COMPONENT EVALUATION
    # the components are evaluated in two ways:
    #   a) the shape of each component must be correlated with the data
    #   b) a minimum peak SNR is required over the length of a transient
    # Note that here we do not use the CNN based classifier, because it was trained on 2p not 1p data

    min_SNR = 2            # adaptive way to set threshold on the transient size
    r_values_min = 0.7    # threshold on space consistency (if you lower more components
    #                        will be accepted, potentially with worst quality)
    cnm.params.set('quality', {'min_SNR': min_SNR,
                               'rval_thr': r_values_min,
                               'use_cnn': False})
    cnm.estimates.evaluate_components(images, cnm.params, dview=dview)

    print(' ***** ')
    print('Number of total components: ', len(cnm.estimates.C))
    print('Number of accepted components: ', len(cnm.estimates.idx_components))
    
    try:
        cnm.estimates.detrend_df_f(quantileMin=5, frames_window=200)
    except:
        pass
    cnm.save(fnames[0].replace('.tif','.hdf5'))
    
    #%% RE-RUN seeded CNMF on accepted patches to refine and perform deconvolution 
    cnm2 = cnm.refit(images, dview=dview)
    cnm2.estimates.evaluate_components(images, cnm2.params, dview=dview)
    try:
        cnm2.estimates.detrend_df_f(quantileMin=5, frames_window=200)
    except:
        pass
    cnm2.save(fnames[0].replace('.tif','b.hdf5'))
    
for file in glob.glob(os.path.join(os.path.dirname(fnames[0]),'*.mmap')):
    os.remove(file)
    
    
job_string = 'find .'+os.path.dirname(fnames[0])+' -type f -name "*mmap" -delete' 
call([job_string],shell=True)