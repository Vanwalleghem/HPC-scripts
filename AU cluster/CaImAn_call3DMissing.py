from subprocess import call
import time
import glob
import os
import sys

fnames_all =[]

with open('Missing_HDF5.txt') as f:
 for line in f: 
  line = line.strip() #or some other preprocessing
  if not "MAX" in line:
   fnames_all.append(line) #storing everything in memory!

fnames_all.sort()

#Create the job array
with open('CaImAn_array.sh','w') as the_file:
 the_file.write('#!/bin/bash \n')
 the_file.write('#SBATCH --account FUNCT_ENS \n')
 the_file.write('#SBATCH --partition normal \n')
 the_file.write('#SBATCH --mem 150G \n')
 the_file.write('#SBATCH  -c 16 \n') 
 the_file.write('#SBATCH  -t 10:0:0 \n')
 the_file.write('#SBATCH  --output=CaImAn_%A_%a.out \n')
 job_string = """#SBATCH --array=1-%s \n""" % (str(len(fnames_all)))
 the_file.write(job_string) 
 job_string = "filename=`sed -n ${SLURM_ARRAY_TASK_ID}p Missing_HDF5.txt` \n"
 the_file.write(job_string) 
 the_file.write('source ~/miniconda3/etc/profile.d/conda.sh\n')
 the_file.write('conda activate caiman\n') 
 the_file.write('export MKL_NUM_THREADS=1\n')
 the_file.write('export OPENBLAS_NUM_THREADS=1\n')
 the_file.write('export VECLIB_MAXIMUM_THREADS=1\n')
 the_file.write('export CAIMAN_TEMP=/faststorage/project/FUNCT_ENS/CaImAnTemp/\n')
 job_string = 'python ~/VolumetricCaImAn1p.py $filename \n' 
 the_file.write(job_string)


job_string = """sbatch CaImAn_array.sh""" 
print(job_string)
call([job_string],shell=True)
