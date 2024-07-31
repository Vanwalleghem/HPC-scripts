from subprocess import call
import time
import glob
import os
import sys

fnames_all =[]
folder=str(sys.argv[1])

base_folder=folder # folder containing the files
for folder in glob.glob(os.path.join(base_folder,'*/')):
 for subfolder in glob.glob(os.path.join(folder,'*/')):
  if not glob.glob(os.path.join(subfolder,'*.hdf5')):
   fnames_all.append(subfolder)
   print(subfolder)
  
fnames_all.sort()

with open('Missing_HDF5.txt', 'w') as f:
    for line in fnames_all:
        f.write("%s\n" % line)