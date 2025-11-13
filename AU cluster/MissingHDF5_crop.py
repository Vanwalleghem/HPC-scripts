from subprocess import call
import time
import glob
import os
import sys

fnames_all =[]
folder=str(sys.argv[1])

base_folder=folder # folder containing the files
list_of_files=glob.glob(os.path.join(base_folder,'**/*_cropped.tif'),recursive=True)
for file_name in list_of_files: 
  if not glob.glob(file_name.replace('.tif','_optCaImAn2.hdf5')):
   fnames_all.append(file_name)
   #print(subfolder)
  
fnames_all.sort()
print(len(fnames_all))

with open('Missing_HDF5.txt', 'w') as f:
    for line in fnames_all:
        f.write("%s\n" % line)