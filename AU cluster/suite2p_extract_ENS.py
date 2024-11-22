import numpy as np
import sys
import os
from suite2p import run_s2p,default_ops
import shutil
import glob
from pathlib import Path
import tifffile

fnames=[os.path.normpath(sys.argv[1])]

# set your options for running
data_path = os.path.normpath(fnames[0])
range2=int(fnames[0].split('range')[-1].split('_')[0])
step=int(fnames[0].split('step')[-1].split('_')[0])
nplanes=int((range2/step)+1);     


ops=default_ops()
ops['fs']=2
ops['tau']=1.6
ops['save_mat']=1
ops['1Preg']=True
ops['denoise']=True
ops['diameter']=[3,4,5]
ops['threshold_scaling']=0.5
ops['max_iterations']=100
ops['smooth_sigma']=8
ops['high_pass']=30
ops['nchannels']=1
ops['block_size']=[64,64]
ops['spatial_taper']=10
ops['spikedetect']=False
ops['pre_smooth']=2
ops['max_iterations']=100
ops['inner_neuropil_radius']=1
ops['neuropil_extract']=0
ops['baseline']='prctile'
ops['nplanes'] = nplanes

file = glob.glob(os.path.join(fnames[0],'*4D2.tif'))
print(data_path+'/suite2p_'+os.path.basename(fnames[0]))

db = {'look_one_level_down': False, # whether to look in ALL subfolders when searching for tiffs
      'data_path': fnames, # a list of folders with tiffs
      'tiff_list': file, # list of tiffs in folder * data_path *!
      'fast_disk': os.environ["TMPDIR"], # string which specifies where the binary file will be stored (should be an SSD)
      'save_folder': os.path.join(data_path,'suite2p_'+ os.path.basename(os.path.normpath(fnames[0])))
     }



tif_mem=tifffile.memmap(file[0])
dims=tif_mem.shape
number_of_frames=1200
frame_dim=next((i for i, elem in enumerate(dims) if elem == number_of_frames),-1) #Looks for dimension matching the number of frames
if frame_dim==0:
 if not os.path.isdir(os.path.join(data_path,'suite2p_'+ os.path.basename(os.path.normpath(fnames[0])))+'/combined'):
  tif_folder=os.path.join(data_path,'Warped_tif')
  Path(tif_folder).mkdir(parents=True, exist_ok=True)
  for frame_nb in range(0,number_of_frames):
   if not os.path.exists(os.path.join(data_path,'Warped_tif',os.path.basename(os.path.normpath(fnames[0]))+'_time'+format(frame_nb, '05d')+'.tif')):
    tif_tosave=tif_mem[frame_nb,:,:,:]
    tifffile.imwrite(os.path.join(data_path,'Warped_tif',os.path.basename(os.path.normpath(fnames[0]))+'_time'+format(frame_nb, '05d')+'.tif'),tif_tosave.transpose((2,0,1)).astype('uint16'),bigtiff=True)
 db['data_path']=os.path.join(data_path,'Warped_tif')
 db['tiff_list']=sorted(glob.glob(os.path.join(data_path,'Warped_tif','*.tif')))
 opsEnd=run_s2p(ops=ops,db=db)
elif frame_dim==3: #frame_nb is at the right spot for a 4D tif file
 #Check if suite2p has already run
 if not os.path.isdir(os.path.join(data_path,'suite2p_'+ os.path.basename(os.path.normpath(fnames[0])))+'/combined'):
  opsEnd=run_s2p(ops=ops,db=db)
  
else:
 print('error in the tif_file '+file[0]) 