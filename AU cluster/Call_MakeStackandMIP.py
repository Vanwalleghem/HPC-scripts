from subprocess import call
import time
import glob
import os
import sys

fnames_all =[]
folder=str(sys.argv[1])
base_folder=os.path.normpath(folder) # folder containing the demo files
for file in glob.glob(os.path.join(base_folder,'*/')): 
 fnames_all.append(file)
fnames_all.sort()

#Create the job array
with open('MakeStacksAndMIP.sh','w') as the_file:
 the_file.write('#!/bin/bash \n')
 the_file.write('#SBATCH --account FUNCT_ENS \n')
 the_file.write('#SBATCH --partition normal \n')
 the_file.write('#SBATCH --mem 32G \n')
 the_file.write('#SBATCH  -c 8 \n') 
 the_file.write('#SBATCH  -t 1-0 \n')
 the_file.write('#SBATCH  --output=StackMIP_%A_%a.out \n')
 job_string = """#SBATCH --array=1-%s \n""" % (str(len(fnames_all)))
 the_file.write(job_string)
 folder=os.path.normpath(base_folder+'/*/')
 job_string = "filename=`ls -d "+folder+" | tail -n ${SLURM_ARRAY_TASK_ID} | head -1` \n"
 the_file.write(job_string) 
 the_file.write('source ~/miniconda3/etc/profile.d/conda.sh\n')
 the_file.write('conda activate greedy \n')
 job_string = 'python ~/MakeStackandMIP.py $filename \n' 
 the_file.write(job_string)


job_string = """sbatch MakeStacksAndMIP.sh""" 
print(job_string)
call([job_string],shell=True)