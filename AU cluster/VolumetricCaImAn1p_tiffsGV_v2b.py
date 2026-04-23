# -*- coding: utf-8 -*-
"""
Created on Thu Dec 19 10:14:31 2024

@author: au691573
"""

import sys
import os

os.environ["KMP_AFFINITY"] = "None"
os.environ["OMP_NUM_THREADS"] = "1"
import glob
#import logging
import numpy as np
import natsort

os.environ["CAIMAN_TEMP"]="/faststorage/project/FUNCT_ENS/CaImAnTemp/"
os.environ['SLURM_SUBMIT_DIR']="/faststorage/project/FUNCT_ENS/CaImAnTemp/"
import caiman as cm
from caiman.source_extraction import cnmf
import cv2
#import datetime
#from pathlib import Path
opencv=True

try:
    cv2.setNumThreads(1)
except:
    pass

tif_file_folder=sys.argv[1]
#tif_file_folder='/faststorage/project/FUNCT_ENS/data/20200729/GV_20200729_fish5_ENS_5DPF_range140_step5_exposure17_power60'
tif_file_folder=tif_file_folder.split('\r')[0]# removes the return to line
fnames=[os.path.normpath(tif_file_folder)]
print(fnames[0])

hdf5_name=os.path.join(fnames[0],os.path.basename(fnames[0])+'_movie.hdf5')

#logger = logging.getLogger("caiman")
#logger.setLevel(logging.DEBUG)
# Set path to logfile
#current_datetime = datetime.datetime.now().strftime("_%Y%m%d_%H%M%S")
#log_filename = 'CaImAn1p' + hdf5_name + '.log'
#log_path = Path(cm.paths.get_tempdir()) / log_filename
# Done with path stuff
#handler = logging.FileHandler(log_path)
#log_format = logging.Formatter("%(relativeCreated)12d [%(filename)s:%(funcName)10s():%(lineno)s] [%(process)d] %(message)s")
#handler.setFormatter(log_format)
#logger.addHandler(handler)

n_processes=2
#%% start a cluster for parallel processing (if a cluster already exists it will be closed and a new session will be opened)

OutputFileAppend='_TifflistNew'

c, dview, n_processes = cm.cluster.setup_cluster(n_processes=n_processes, single_thread=False)

#print(hdf5_name)
#hdf5_name=hdf5_name[0].replace('.tif','_movie.hdf5')

List_files=sorted(glob.glob(os.path.join(fnames[0],'3Dreg/*Warped3.tif')))
#print(hdf5_name)
if len(List_files)<1200:
 print('not enough warped3.tif files, switching to warped2')
 #List_files=sorted(glob.glob(os.path.join(fnames[0],'3Dreg/*Warped2*.tif')))
 List_files=sorted(glob.glob(os.path.join(fnames[0],'3Dreg/*Warped2.tif'))) 
 if len(List_files)<1200:
  print('not enough warped2.tif files either')
  exit()

List_files=[file_name for file_name in List_files if "template" not in file_name]
List_files=natsort.natsorted(List_files)

if hdf5_name:
 if glob.glob(hdf5_name.replace('_movie.hdf5',OutputFileAppend+'.hdf5')):
  print("Folder is done")
  exit()

print('Number of Tifs is: ' + str(len(List_files)))
if len(List_files)>1200:
    List_files=[filename for filename in List_files if "RS" in os.path.basename(filename)]
    if len(List_files)>1200:
     sys.exit("Too many tif files in: "+fnames[0])
#hdf5_name=hdf5_name[0].replace('.tif','_movie.hdf5')

if not glob.glob(hdf5_name):
 cm.load(List_files,outtype=np.uint16, is3D=True).save(hdf5_name)

print(hdf5_name)
fname2 = [hdf5_name]
try:
    Y= cm.load(hdf5_name)
except:
    Y=cm.load(List_files,outtype=np.uint16, is3D=True)


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
frate = 2                       # movie frame rate
#                     else it is set automatically
min_corr = .7       # min peak value from correlation image
min_pnr = 8        # min peak to noise ration from PNR image
ssub_B = 3          # additional downsampling factor in space for background
ring_size_factor = 1.6  # radius of ring is gSiz*ring_size_factor
file_name=os.path.join('/faststorage/project/FUNCT_ENS/CaImAnTemp/',os.path.basename(hdf5_name)+'temp.hdf5')
opts = cnmf.params.CNMFParams(params_dict={
								'is3D':False,
								'method_init': 'corr_pnr',  # use this for 1 photon
								'K': K,
								'gSig': gSig,
								#'gSiz': (4 * gSig + 1, 4 * gSig + 1),
								'merge_thr': merge_thr,
								'p': p,
								'fr':frate,
								'decay_time':1.8,
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


# dataset dependent parameters

decay_time = 1.5                 # length of a typical transient in seconds
# motion correction parameters
motion_correct = True    # flag for performing motion correction
pw_rigid = True         # flag for performing piecewise-rigid motion correction (otherwise just rigid)
gSig_filt = (5,5)#(5, 5, 3)       # size of high pass spatial filtering, used in 1p data
max_shifts = (5, 5)      # maximum allowed rigid shift
strides = (48, 48)       # start a new patch for pw-rigid motion correction every x pixels
overlaps = (12, 12)      # overlap between pathes (size of patch strides+overlaps)
max_deviation_rigid = None  # maximum deviation allowed for patch with respect to rigid shifts
border_nan = 'copy'      # replicate values along the boundaries
num_frames_split = 200
mc_dict = {    
    'fr': frate,
    'decay_time': decay_time,
    'pw_rigid': pw_rigid,    
    'gSig_filt': gSig_filt,
    'strides': strides,
    'overlaps': overlaps,
    'max_deviation_rigid': max_deviation_rigid,
    'border_nan': border_nan,
    'gnb': 0,
    'shifts_opencv':True,
    'nonneg_movie':True,
    'max_shifts': max_shifts,
    'num_frames_split' : num_frames_split
}
opts.change_params(params_dict=mc_dict)

for slice_nb in range(1,Y.shape[-1]):
    temp=[np.squeeze(Y[:,:,:,slice_nb])]
    fname_new = cm.save_memmap(temp,base_name=str(slice_nb)+hdf5_name[0:10], order='C',border_to_0=0, dview=dview)
    Yr, dims, T = cm.load_memmap(fname_new)
    Yr = np.reshape(Yr.T, [T] + list(dims), order='F')
    opts.change_params({'fnames':fname_new})
    cnm = cnmf.CNMF(n_processes, params=opts, k=K, gSig=gSig, merge_thresh=merge_thr, p=p,dview=dview,rf=rf,stride=stride_cnmf,only_init_patch=True)
    try:
        if not glob.glob(hdf5_name.replace('.tif',OutputFileAppend+'_Slice'+str(slice_nb)+'_Temp.hdf5')):
            cnm.fit_file()
            cnm.save(hdf5_name.replace('.tif',OutputFileAppend+'_Slice'+str(slice_nb)+'_Temp.hdf5'))
            min_SNR = 2            # adaptive way to set threshold on the transient size
            r_values_min = 0.6    # threshold on space consistency (if you lower more components
            #                        will be accepted, potentially with worst quality)
            cnm.params.set('quality', {'min_SNR': min_SNR,'rval_thr': r_values_min,'use_cnn': False})
            cnm.estimates.evaluate_components(Yr, cnm.params, dview=dview)
            print(' ***** ')
            print('Number of total components: ', len(cnm.estimates.C))
            print('Number of accepted components: ', len(cnm.estimates.idx_components))
            cnm.save(hdf5_name.replace('.tif',OutputFileAppend+'_Slice'+str(slice_nb)+'.hdf5'))
            #%% RE-RUN seeded CNMF on accepted patches to refine and perform deconvolution 
            cnm2 = cnm.refit(Yr, dview=dview)
            cnm2.estimates.evaluate_components(Yr, cnm2.params, dview=dview)
            cnm2.save(hdf5_name.replace('.tif',OutputFileAppend+'_Slice'+str(slice_nb)+'b.hdf5'))
    except:
        print('error with slice number: '+str(slice_nb))