from subprocess import call
import time
import glob
import os
import sys

fnames_all =[]
folder=str(sys.argv[1])
base_folder=folder 
#You will need to change the 'GV*/' with something that covers all your folders
for file in glob.glob(os.path.join(base_folder,'*/')): 
 fnames_all.append(file)
fnames_all.sort()

#Create the job array in a file, then calls the job
with open('Greedy_3D.sh','w') as the_file:
 the_file.write('#!/bin/bash \n')
 the_file.write('#SBATCH --account Student_ENS \n')
 the_file.write('#SBATCH --partition normal \n')
 the_file.write('#SBATCH --mem 100G \n')
 the_file.write('#SBATCH  -c 16 \n') 
 the_file.write('#SBATCH  -t 1-0 \n')
 the_file.write('#SBATCH  --output=Greedy_3D%A_%a.out \n')
 job_string = """#SBATCH --array=1-%s \n""" % (str(len(fnames_all)))
 the_file.write(job_string) 
 #You will need to change the 'GV*/' with something that covers all your folders
 job_string = 'filename=`ls -d '+base_folder+'/*/ | tail -n +\${SLURM_ARRAY_TASK_ID} | head -1` \n'
 the_file.write(job_string) 
 #You will need to check that the below folder is where the conda.sh is found
 the_file.write('source ~/miniconda3/etc/profile.d/conda.sh\n')
 the_file.write('conda activate greedy \n')
 job_string = 'python ~/Greedy_MC_3Dstack_Pierre.py $filename \n' 
 the_file.write(job_string)


job_string = """sbatch Greedy_3D.sh""" 
print(job_string)
call([job_string],shell=True)
