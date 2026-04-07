from subprocess import call
import glob
import os
import sys

fnames_all =[]
base_folder=str(sys.argv[1]) 

#for file1 in glob.glob(os.path.join(base_folder,'**/3Dreg/'),recursive=True): 
for file1 in glob.glob(os.path.join(base_folder,'**/*Jacobian*.npy'),recursive=True):
 #file1=os.path.normpath(file1.split('/3Dreg')[0])
 fnames_all.append(file1)
fnames_all.sort()

Script_file='XmapGCaMPJacob'
with open('XMap.txt', 'w') as f:
    for line in fnames_all:
        f.write("%s\n" % line)
# for line in f: 
#  line = line.strip()
  #print(line)
#  if not "MAX" in line:
#   fnames_all.append(line) /faststorage/project/FUNCT_ENS/data/

#Create the job array
with open(Script_file+'.sh','w') as the_file:
 the_file.write('#!/bin/bash \n')
 the_file.write('#SBATCH --account FUNCT_ENS \n')
 the_file.write('#SBATCH --partition normal \n')
 the_file.write('#SBATCH --mem 16G \n')
 the_file.write('#SBATCH  -c 4 \n') 
 the_file.write('#SBATCH  -t 01:00:00 \n')
 the_file.write('#SBATCH  --output='+Script_file+'_%A_%a.out \n')
 job_string = """#SBATCH --array=1-%s \n""" % (str(len(fnames_all)))
 the_file.write(job_string) 
 #job_string = 'filename=`ls -d '+os.path.join(base_folder,'*.hdf5')+' | tail -n +\\${SLURM_ARRAY_TASK_ID} | head -1` \n'
 job_string = "filename=`sed -n ${SLURM_ARRAY_TASK_ID}p XMap.txt` \n"
 the_file.write(job_string) 
 the_file.write('source ~/miniforge3/etc/profile.d/conda.sh\n')
 the_file.write('conda activate caiman \n')
 job_string = 'python ~/'+Script_file+'.py $filename \n' 
 the_file.write(job_string)


job_string = "sbatch "+Script_file+".sh" 
print(job_string)
call([job_string],shell=True)
