from subprocess import call
import glob
import os
import sys

fnames_all =[]
folder=str(sys.argv[1])
base_folder=folder # folder containing the demo files
for file in glob.glob(os.path.join(base_folder,'SBF*/')): 
 fnames_all.append(file)
fnames_all.sort()

#Create the job array
with open('BadWarp.sh','w') as the_file:
 the_file.write('#!/bin/bash \n')
 the_file.write('#SBATCH --account Opt_Tweezers \n')
 the_file.write('#SBATCH --partition normal \n')
 the_file.write('#SBATCH --mem 80G \n')
 the_file.write('#SBATCH  -c 16 \n') 
 the_file.write('#SBATCH  -t 20:0:0 \n')
 the_file.write('#SBATCH  --output=4DWarp_%A_%a.out \n')
 job_string = """#SBATCH --array=1-%s \n""" % (str(len(fnames_all)))
 the_file.write(job_string) 
 job_string = 'filename=`ls -d '+base_folder+'/SBF_*/ | tail -n +\${SLURM_ARRAY_TASK_ID} | head -1` \n'
 the_file.write(job_string)  
 the_file.write('source ~/miniconda3/etc/profile.d/conda.sh\n')
 the_file.write('conda activate greedy\n') 
 job_string = 'python ~/Warp4D2_SBF.py $filename \n' 
 the_file.write(job_string)

job_string = """sbatch BadWarp.sh""" 
print(job_string)
call([job_string],shell=True)
