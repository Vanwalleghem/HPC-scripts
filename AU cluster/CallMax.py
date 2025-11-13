from subprocess import call
import time
import glob
import os
import sys

fnames_all =[]
folder=str(sys.argv[1])
base_folder=folder # folder containing the demo files
for file in glob.glob(os.path.join(base_folder,'*/')): 
 fnames_all.append(file)
fnames_all.sort()

#Create the job array
with open('MIP_ENS.sh','w') as the_file:
 the_file.write('#!/bin/bash \n')
 the_file.write('#SBATCH --account FUNCT_ENS \n')
 the_file.write('#SBATCH --partition normal \n')
 the_file.write('#SBATCH --mem 16G \n')
 the_file.write('#SBATCH  -c 4 \n') 
 the_file.write('#SBATCH  -t 0-2 \n')
 the_file.write('#SBATCH  --output=MIP_ENS_%A_%a.out \n')
 job_string = """#SBATCH --array=1-%s \n""" % (str(len(fnames_all)))
 the_file.write(job_string) 
 job_string = "filename=`ls -d "+base_folder+"/* | tail -n +${SLURM_ARRAY_TASK_ID} | head -1` \n" 
 #job_string = "filename=`sed -n ${SLURM_ARRAY_TASK_ID}p FoldersToReprocess.txt` \n"
 the_file.write(job_string) 
 the_file.write('source ~/miniforge3/etc/profile.d/conda.sh\n') 
 the_file.write('conda init\n') 
 the_file.write('conda activate greedy\n') 
 job_string = 'python ~/MIP_ENS.py $filename \n' 
 the_file.write(job_string)


job_string = """sbatch MIP_ENS.sh""" 
print(job_string)
call([job_string],shell=True)
