from subprocess import call
import glob
import os
import sys

folder=str(sys.argv[1])

#Create the job array
with open('BadWarp.sh','w') as the_file:
 the_file.write('#!/bin/bash \n')
 the_file.write('#SBATCH --account STUDENT_ENS \n')
 the_file.write('#SBATCH --partition normal \n')
 the_file.write('#SBATCH --mem 40G \n')
 the_file.write('#SBATCH  -c 16 \n') 
 the_file.write('#SBATCH  -t 20:0:0 \n')
 the_file.write('#SBATCH  --output=BadWarp_%A_%a.out \n') 
 the_file.write('source ~/miniforge3/etc/profile.d/conda.sh\n') 
 the_file.write('conda init\n')
 the_file.write('conda activate greedy\n') 
 job_string = 'python ~/Fix4D2_BadWarp.py '+folder+'\n' 
 the_file.write(job_string)

job_string = """sbatch BadWarp.sh""" 
print(job_string)
call([job_string],shell=True)
