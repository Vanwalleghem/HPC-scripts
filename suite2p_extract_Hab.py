import numpy as np
import sys
import os
from suite2p import run_s2p
import shutil
import glob
fnames=[sys.argv[1]]
final_frate=4#int(os.environ["FPS"]) # frame rate in Hz
import faulthandler; faulthandler.enable()

# set your options for running
ops = np.load('./ops_1P_ENS.npy',allow_pickle=True).item()
data_path = os.path.dirname(fnames[0])

ops['nchannels'] = 1
ops['fs'] = final_frate
ops['sparse_mode']=False
ops['nonrigid']=False

print(data_path+'/suite2p_'+os.path.basename(fnames[0]))
#Check if suite2p has already run
if not os.path.isfile(data_path+'/suite2p_'+os.path.basename(fnames[0]).replace('.tif','')+'/plane0/F.npy'):
    #for file in glob.glob(os.path.join(data_path,'*.tif')):        
    db = {'look_one_level_down': False, # whether to look in ALL subfolders when searching for tiffs
          'data_path': [data_path], # a list of folders with tiffs 
                                                 # (or folder of folders with tiffs if look_one_level_down is True, or subfolders is not empty)         
          'fast_disk': os.environ["TMPDIR"], # string which specifies where the binary file will be stored (should be an SSD)
          'tiff_list': [fnames[0],fnames[0].replace('media1','media3')], # list of tiffs in folder * data_path *!
          'save_folder': data_path+'/suite2p_'+os.path.basename(fnames[0]).replace('.tif','')
        }
    # run one experiment

    opsEnd=run_s2p(ops=ops,db=db)
