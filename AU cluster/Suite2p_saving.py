import sys
import os
import shutil
from pathlib import Path

Dir_processing='/faststorage/project/FUNCT_ENS/data'
Dir_saving='/faststorage/project/FUNCT_ENS/data/Done'
Dir_saving=os.path.normpath(Dir_saving)

for path in Path(os.path.normpath(Dir_processing)).rglob('*/combined/Fall.mat'):
    extracted_filename=os.path.basename(str(path).split('/combined/')[0])
    extracted_dirname=os.path.dirname(str(path).split('/combined/')[0])
    extracted_filename=extracted_filename.split('suite2p_')[1]
    shutil.copy(str(path), Dir_saving+'/'+extracted_filename+'.mat')
    print("File copied successfully.")