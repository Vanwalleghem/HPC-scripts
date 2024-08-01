import time
import glob
import os
import sys
import tifffile

FourD_Files = glob.glob('/faststorage/project/FUNCT_ENS/NewENSDataAU/**/*_4D2.tif', recursive=True)

Problem_files=[]
Broken_files=[]

for FourD_File in FourD_Files:
 try:
  testFile = tifffile.TiffFile(FourD_File)
 except:
  Broken_files.append(FourD_File) 
 if not testFile.pages[0].dtype == 'uint16': 
  Problem_files.append(FourD_File)

len(Problem_files)
