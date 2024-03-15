from CheckFilesAndFix import CheckFilesAndFix
import glob
import os
import sys

tif_file_folder=sys.argv[1]
print(tif_file_folder)
tif_list=glob.glob(tif_file_folder+'/*.tif')
tif_list.sort()
print('List of files is '+str(len(tif_list))+' long')
print(tif_list)
CheckFilesAndFix(tif_file_folder)


