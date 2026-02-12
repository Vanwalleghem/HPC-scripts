from subprocess import call
import glob
import os
import sys

fnames_all =[]
folder=str(sys.argv[1])

base_folder=folder # folder containing the demo files
for file in glob.glob(os.path.join(base_folder,'**/3Dreg/'),recursive=True): 
 fnames_all.append(file)
fnames_all.sort()

with open('ToConvert.txt', 'w') as f:
    for line in fnames_all:
        f.write("%s\n" % line.split('/3Dreg')[0])

#with open('FoldersToReprocess.txt') as f:
# for line in f: 
#  line = line.strip() #or some other preprocessing
#  if not "MAX" in line:
#   fnames_all.append(line) #storing everything in memory!

#fnames_all.sort()


#Create the job array
with open('Convert_array.sh','w') as the_file:
 the_file.write('#!/bin/bash \n')
 the_file.write('#SBATCH --account FUNCT_ENS \n')
 the_file.write('#SBATCH --partition normal \n')
 the_file.write('#SBATCH --mem 8G \n')
 the_file.write('#SBATCH  -c 2 \n') 
 the_file.write('#SBATCH  -t 5:0:0 \n')
 the_file.write('#SBATCH  --output=Convert_%A_%a.out \n')
 job_string = """#SBATCH --array=1-%s \n""" % (str(len(fnames_all)))
 the_file.write(job_string) 
 #job_string = 'filename=`ls -d '+base_folder+'/*/ | tail -n +\${SLURM_ARRAY_TASK_ID} | head -1` \n'
 job_string = "filename=`sed -n ${SLURM_ARRAY_TASK_ID}p ToConvert.txt` \n"
 the_file.write(job_string) 
 the_file.write('source ~/miniforge3/etc/profile.d/conda.sh\n') 
 the_file.write('conda init\n') 
 the_file.write('conda activate greedy\n') 
 #the_file.write(job_string)  
 job_string = 'python ~/Convert_NiiToTiff.py $filename \n' 
 the_file.write(job_string)


job_string = """sbatch Convert_array.sh""" 
print(job_string)
call([job_string],shell=True)
