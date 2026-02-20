# -*- coding: utf-8 -*-
"""
Created on Thu Dec 19 10:14:31 2024

@author: au691573
"""

import sys
import os

os.environ["KMP_AFFINITY"] = "disabled"
os.environ["OMP_NUM_THREADS"] = "1"
#import shutil
import glob
import logging
import numpy as np
import natsort
import gc

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
FourD_File = os.path.basename(fnames[0])

logger = logging.getLogger("caiman")
logger.setLevel(logging.DEBUG)
# Set path to logfile
current_datetime = datetime.datetime.now().strftime("_%Y%m%d_%H%M%S")
log_filename = 'CaImAn1p' + FourD_File + '.log'
log_path = Path(cm.paths.get_tempdir()) / log_filename
# Done with path stuff
handler = logging.FileHandler(log_path)
log_format = logging.Formatter("%(relativeCreated)12d [%(filename)s:%(funcName)10s():%(lineno)s] [%(process)d] %(message)s")
handler.setFormatter(log_format)
logger.addHandler(handler)

n_processes=1
#%% start a cluster for parallel processing (if a cluster already exists it will be closed and a new session will be opened)

OutputFileAppend='_TifflistNew'

c, dview, n_processes = cm.cluster.setup_cluster( n_processes=n_processes, single_thread=False)

#print(FourD_File)
#hdf5_name=FourD_File[0].replace('.tif','_movie.hdf5')
hdf5_name=os.path.join(fnames[0],FourD_File+'_movie.hdf5')
List_files=sorted(glob.glob(os.path.join(fnames[0],'3Dreg/*RS*Warped3.tif')))
print(hdf5_name)
if len(List_files)<1200:
 print('not enough warped3.tif files, switching to warped2')
 #List_files=sorted(glob.glob(os.path.join(fnames[0],'3Dreg/*Warped2*.tif')))
 List_files=sorted(glob.glob(os.path.join(fnames[0],'3Dreg/*RS*Warped2.tif')))
 with open('ToCheckCaiman.txt', 'a') as f:  
  f.write("%s\n" % fnames[0])
 if len(List_files)<1200:
  print('not enough warped2.tif files either')
  exit()
 
 
List_files=[file_name for file_name in List_files if "template" not in file_name]
#List_number=[int(file_name.split('time')[1].split('.tif')[0]) for file_name in List_files if "template" not in file_name]
#List_number=[int(file_name.split('_power')[-1].split('_')[1].split('.tif')[0]) for file_name in List_files if "template" not in file_name]

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
 if glob.glob(FourD_File.replace('.tif',OutputFileAppend+'.hdf5')):
  print("Folder is done")
  exit()

print('Number of Tifs is: ' + str(len(List_files)))
if len(List_files)>1200:
    List_files=[filename for filename in List_files if "RS" in os.path.basename(filename)]
    if len(List_files)>1200:
     sys.exit("Too many tif files in: "+fnames[0])
#hdf5_name=FourD_File[0].replace('.tif','_movie.hdf5')
if not glob.glob(hdf5_name):
 cm.load(List_files, is3D=True).save(hdf5_name) 

fname2 = [hdf5_name]

# dataset dependent parameters
frate = 2                       # movie frame rate
decay_time = 1.5                 # length of a typical transient in seconds
# motion correction parameters
motion_correct = True    # flag for performing motion correction
pw_rigid = True         # flag for performing piecewise-rigid motion correction (otherwise just rigid)
gSig_filt = None#(5, 5, 3)       # size of high pass spatial filtering, used in 1p data
max_shifts = (5, 5, 2)      # maximum allowed rigid shift
strides = (48, 48, 4)       # start a new patch for pw-rigid motion correction every x pixels
overlaps = (12, 12, 2)      # overlap between pathes (size of patch strides+overlaps)
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
    'is3D': True,
    'max_shifts': max_shifts,
    'num_frames_split' : num_frames_split
}

opts = cnmf.params.CNMFParams(params_dict=mc_dict)
file_to_save=os.path.join(tif_file_folder,'mem_file_RS.txt')
if os.path.exists(file_to_save):
   with open(file_to_save, 'r') as f:
    lines = f.readlines()
    mmap_filename=lines[0].split('\r')[0]# removes the return to line
    mmap_filename = r"{}".format(mmap_filename)
    if os.path.exists(mmap_filename):
     Yr, dims, T = cm.load_memmap(mmap_filename)
    else:
     mc = cm.motion_correction.MotionCorrect(fname2, dview=dview, **opts.get_group('motion'))
     try:
         print('1')
         mc.motion_correct(save_movie=True)  
     except:
         time.sleep(10)
         print('2')
         #if not glob.glob(os.path.join('/faststorage/project/FUNCT_ENS/CaImAnTemp/',os.path.basename(FourD_File[0]).replace('.tif','*.mmap'))):
         mc = cm.motion_correction.MotionCorrect(fname2, dview=dview, **opts.get_group('motion'))
         mc.motion_correct(save_movie=True)
     fname_new2 = cm.save_memmap(mc.mmap_file, base_name='memmap_'+FourD_File, order='C',border_to_0=0, dview=dview) # exclude borders
     with open(file_to_save, 'w') as f:
      f.write(str(fname_new2))
     Yr, dims, T = cm.load_memmap(fname_new2)
else:
    mc = cm.motion_correction.MotionCorrect(fname2, dview=dview, **opts.get_group('motion'))
    try:
        print('1')
        mc.motion_correct(save_movie=True)  
    except:
        time.sleep(10)
        print('2')
        #if not glob.glob(os.path.join('/faststorage/project/FUNCT_ENS/CaImAnTemp/',os.path.basename(FourD_File[0]).replace('.tif','*.mmap'))):
        mc = cm.motion_correction.MotionCorrect(fname2, dview=dview, **opts.get_group('motion'))
        mc.motion_correct(save_movie=True)
    fname_new2 = cm.save_memmap(mc.mmap_file, base_name='memmap_'+FourD_File, order='C',border_to_0=0, dview=dview) # exclude borders
    with open(file_to_save, 'w') as f:
     f.write(str(fname_new2))
    Yr, dims, T = cm.load_memmap(fname_new2)
     

print('dimensions :', dims, '. Number of frames :',T)
if (T<1000):
 print('problem with dimensions')
 exit() 
 
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
del Yr
gc.collect()  

n_processes=1
#%% restart cluster to clean up memory
cm.stop_server(dview=dview)
c, dview, n_processes = cm.cluster.setup_cluster(
     n_processes=n_processes, single_thread=True)
n_processes=1
# set parameters
rf = 30  # half-size of the patches in pixels. rf=25, patches are 50x50
stride = 10  # amount of overlap between the patches in pixels
K = 100  # number of neurons expected per patch
gSig = [4, 4, 2]  # expected half size of neurons
merge_thr = 0.7  # merging threshold, max correlation allowed
p = 1  # order of the autoregressive system
tsub = 1            # downsampling factor in time for initialization,
ssub = 1            # downsampling factor in space for initialization,
#min_pnr = 8        # min peak to noise ration from PNR image
min_pnr = 4        # min peak to noise ration from PNR image
min_SNR = 2
ssub_B = 4          # additional downsampling factor in space for background
gnb = -1
#min_corr=0.85
min_corr=0.6
ring_size_factor = 1.4  # radius of ring is gSiz*ring_size_factor
rval_thr = 0.6   # accept components with space correlation threshold or higher
print('set')

opts = cnmf.params.CNMFParams(params_dict={
 'K': K,
 'is3D': True,
 'fr': frate,
 'gSig': gSig,                   
 'merge_thr': merge_thr,
 'decay_time': decay_time,
 'p': p,
 'tsub': tsub,
 'ssub': ssub, 
 'use_cnn':True, 
 'only_init': True,    # set it to True to run CNMF-E
 'noise_method':'median',
 'method_deconvolution': 'oasis',       # could use 'cvxpy' alternatively        
 'update_background_components': False,
 'method_init': 'greedy_roi', #'corr_pnr',                             
 'min_pnr': min_pnr,
 'min_SNR': min_SNR,
 'min_corr': min_corr,
 'normalize_init': False,               # just leave as is
 'in_memory':False,
 'rval_thr': rval_thr,
 'center_psf': True,                    # leave as is for 1 photon
 'ssub_B': ssub_B, 
 'init_batch': 200,
 'n_pixels_per_process' : 10000,
 'ring_size_factor': ring_size_factor,
 'del_duplicates': True,                # whether to remove duplicates from initialization
 'gnb':gnb,
 'strides':(60,60,6),
 'overlaps':(20,20,2),
 'use_hals':False,
 'border_pix': 0})                # The parameter border pix must be set to 0 for 3D data since border removal is not implemented)

cnm = cnmf.CNMF(n_processes, params=opts, k=K, gSig=gSig, merge_thresh=merge_thr, p=p,dview=dview,rf=rf,stride=stride,only_init_patch=True)
cnm.params.set('spatial', {'se': np.ones((3,3,1), dtype=np.uint8)})
                
#cnm.params.set('spatial', {'se': np.ones((3,3,1), dtype=np.uint8)})

cnm = cnm.fit(images) #could look into replacing with fit_file

 
cnm.save(hdf5_name.replace('_movie.hdf5',OutputFileAppend+'Temp.hdf5'))

min_SNR = 2            # adaptive way to set threshold on the transient size
r_values_min = 0.5    # threshold on space consistency (if you lower more components
#                        will be accepted, potentially with worst quality)
cnm.params.set('quality', {'min_SNR': min_SNR,'rval_thr': r_values_min,'use_cnn': False})
cnm.estimates.evaluate_components(images, cnm.params, dview=dview)

print(' ***** ')
print(f"Number of total components: {len(cnm.estimates.C)}")
print(f"Number of accepted components: {len(cnm.estimates.idx_components)}")

#try:
#    cnm.estimates.detrend_df_f(quantileMin=5, frames_window=200)
#except:
#    pass
cnm.save(hdf5_name.replace('_movie.hdf5',OutputFileAppend+'.hdf5'))
cnm2 = cnm.refit(images, dview=dview)
cnm2.estimates.evaluate_components(images, cnm2.params, dview=dview)

print(' ***** ')
print(f"Number of total components: {len(cnm2.estimates.C)}")
print(f"Number of accepted components: {len(cnm2.estimates.idx_components)}")

cnm2.save(hdf5_name.replace('_movie.hdf5',OutputFileAppend+'b.hdf5'))

cm.stop_server(dview=dview)
os.remove(mc.mmap_file[0])