from subprocess import call
import sys
import glob
import os

fnames_all =[]

#with open('FoldersToReprocess.txt') as f:
# for line in f: 
  #line = line.strip() #or some other preprocessing
  #if not "MAX" in line:
   #fnames_all.append(line) #storing everything in memory!

fnames_all =[]
folder=str(sys.argv[1])
base_folder=folder # folder containing the demo files
for file in glob.glob(os.path.join(base_folder,'*/')): 
 fnames_all.append(file)
fnames_all.sort()

fnames_all.sort()

#Create the job array
with open('Greedy3_array.sh','w') as the_file:
 the_file.write('#!/bin/bash \n')
 the_file.write('#SBATCH --account FUNCT_ENS \n')
 the_file.write('#SBATCH --partition normal \n')
 the_file.write('#SBATCH --mem 64G \n')
 the_file.write('#SBATCH  -c 16 \n') 
 the_file.write('#SBATCH  -t 3-0 \n')
 the_file.write('#SBATCH  --output=CaImAn_%A_%a.out \n')
 job_string = """#SBATCH --array=1-%s \n""" % (str(len(fnames_all)))
 the_file.write(job_string) 
 job_string = "filename=`sed -n ${SLURM_ARRAY_TASK_ID}p FoldersToReprocess.txt` \n"
 the_file.write(job_string) 
 the_file.write('source ~/miniconda3/etc/profile.d/conda.sh\n')
 the_file.write('conda activate greedy\n')  
 the_file.write('export CAIMAN_TEMP=/faststorage/project/FUNCT_ENS/CaImAnTemp/\n')
 job_string = 'python ~/Greedy_MC_3Dstack_Third.py $filename \n' 
 the_file.write(job_string)


job_string = """sbatch Greedy3_array.sh""" 
print(job_string)
call([job_string],shell=True)
