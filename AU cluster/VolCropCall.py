from subprocess import call
import time
import glob
import os
import sys

fnames_all =[]
folder=str(sys.argv[1])

base_folder=folder # folder containing the demo files
for file1 in glob.glob(os.path.join(base_folder,'**/3Dreg/'),recursive=True): 
 file1=os.path.normpath(file1.split('/3Dreg')[0])
 fnames_all.append(file1)
fnames_all.sort()


with open('TiffFileRScrop.txt', 'w') as f:
    for line in fnames_all:
        f.write("%s\n" % line)


#with open('FoldersToReprocess.txt') as f:
# for line in f: 
#  line = line.strip() #or some other preprocessing
#  if not "MAX" in line:
#   fnames_all.append(line) #storing everything in memory!

fnames_all.sort()

#Create the job array
with open('CaImAn_array.sh','w') as the_file:
 the_file.write('#!/bin/bash \n')
 the_file.write('#SBATCH --account FUNCT_ENS \n')
 the_file.write('#SBATCH --partition normal \n')
 the_file.write('#SBATCH --mem 200G \n')
 the_file.write('#SBATCH  -c 16 \n') 
 the_file.write('#SBATCH  -t 1-0 \n')
 the_file.write('#SBATCH  --output=CaImAn_%A_%a.out \n')
 job_string = """#SBATCH --array=1-%s \n""" % (str(len(fnames_all)))
 the_file.write(job_string) 
 #job_string = 'filename=`ls -d '+base_folder+'/*/ | tail -n +\\${SLURM_ARRAY_TASK_ID} | head -1` \n'
 job_string = "filename=`sed -n ${SLURM_ARRAY_TASK_ID}p TiffFileRScrop.txt` \n"
 the_file.write(job_string)
 the_file.write('source ~/miniforge3/etc/profile.d/conda.sh\n') 
 the_file.write('conda init\n')
 the_file.write('conda activate caiman\n') 
 the_file.write('export MKL_NUM_THREADS=1\n')
 the_file.write('export OPENBLAS_NUM_THREADS=1\n')
 the_file.write('export VECLIB_MAXIMUM_THREADS=1\n')
 the_file.write('export KMP_AFFINITY=disabled\n')  
 the_file.write('export CAIMAN_TEMP=/faststorage/project/FUNCT_ENS/CaImAnTemp/\n')
 job_string = 'python ~/VolumetricCropped.py $filename \n' 
 the_file.write(job_string)


job_string = """sbatch CaImAn_array.sh""" 
print(job_string)
call([job_string],shell=True)
