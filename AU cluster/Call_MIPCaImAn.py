from subprocess import call
import glob
import os
import sys

#fnames_all =[]
folder=str(sys.argv[1])

base_folder=folder # folder containing the demo files
#for file in glob.glob(os.path.join(base_folder,'*_Max.tif')): 
 #fnames_all.append(file)
#fnames_all.sort()

fnames_all=glob.glob(os.path.join(base_folder,'*_Max.tif'))

with open('ToConvert.txt', 'w') as f:
    for line in fnames_all:
        f.write("%s\n" % line)


#Create the job array
with open('Convert_array.sh','w') as the_file:
 the_file.write('#!/bin/bash \n')
 the_file.write('#SBATCH --account FUNCT_ENS \n')
 the_file.write('#SBATCH --partition normal \n')
 the_file.write('#SBATCH --mem 100G \n')
 the_file.write('#SBATCH  -c 4 \n') 
 the_file.write('#SBATCH  -t 20:0:0 \n')
 the_file.write('#SBATCH  --output=MIP_%A_%a.out \n')
 job_string = """#SBATCH --array=1-%s \n""" % (str(len(fnames_all)))
 the_file.write(job_string) 
 #job_string = 'filename=`ls -d '+base_folder+'/*/ | tail -n +\${SLURM_ARRAY_TASK_ID} | head -1` \n'
 job_string = "filename=`sed -n ${SLURM_ARRAY_TASK_ID}p ToConvert.txt` \n"
 the_file.write(job_string)
 the_file.write('source ~/miniforge3/etc/profile.d/conda.sh\n') 
 the_file.write('conda init\n')
 the_file.write('conda activate caiman\n') 
 the_file.write('export MKL_NUM_THREADS=1\n')
 the_file.write('export OPENBLAS_NUM_THREADS=1\n')
 the_file.write('export VECLIB_MAXIMUM_THREADS=1\n')
 the_file.write('export KMP_AFFINITY=disabled\n')  
 the_file.write('export CAIMAN_TEMP=/faststorage/project/FUNCT_ENS/CaImAnTemp/\n')
 job_string = 'python ~/MIPCaImAn.py $filename \n' 
 the_file.write(job_string)


job_string = """sbatch Convert_array.sh""" 
print(job_string)
call([job_string],shell=True)
