from subprocess import call
import glob
import os
import sys

fnames_all =[]
folder=str(sys.argv[1])

base_folder=folder # folder containing the files
list_of_files=glob.glob(os.path.join(base_folder,'**/'))
for file_name in list_of_files: 
  if not glob.glob(os.path.join(file_name,'_Tifflist.hdf5')):
   fnames_all.append(os.path.dirname(file_name))
   #print(subfolder)
  
fnames_all.sort()
print(len(fnames_all))

for folder in fnames_all:
  job_string='python CaImAn_callTiffs.py '+folder
  print(job_string)
  call([job_string],shell=True)