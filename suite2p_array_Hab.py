from subprocess import call
import time
import glob
import os
import sys

fnames_all =[]
folder=str(sys.argv[1])
fps=str(sys.argv[2])

base_folder='/QRISdata'+folder # folder containing the demo files
for file in glob.glob(os.path.join(base_folder,'*media1*.tif')):
    if file.endswith(".tif") and not file.endswith("_mean.tif"):
        fnames_all.append(file)
fnames_all = [x for x in fnames_all if os.path.isfile(x)]
fnames_all.sort()

#Create the job array

with open('ArraySuite2p.pbs','w') as the_file:
    the_file.write('#!/bin/bash \n')
    the_file.write('#PBS -A UQ-SCI-SBMS \n')
    the_file.write('#PBS -l select=1:ncpus=10:mem=50GB:vmem=50GB \n')
    the_file.write('#PBS -l walltime=5:00:00 \n')
    the_file.write('#PBS -j oe \n')
    job_string = """#PBS -t 1-%s \n""" % (str(len(fnames_all)))
    the_file.write(job_string)
    job_string = 'filename=`find '+base_folder+' -type f -name ''*media1*.tif'' -exec ls -1 {} \; | tail -n +\${PBS_ARRAY_INDEX} | head -1` \n'
    the_file.write(job_string)
    the_file.write('/usr/local/bin/recall_medici $filename \n')
    the_file.write('module load anaconda \n')
    the_file.write('source activate suite2p \n')
    job_string = 'python ~/suite2p_extract_Hab.py $filename \n' 
    the_file.write(job_string)
 
#Now do some things
os.environ["FPS"]=fps
job_string = """qsub -v FPS=%s ArraySuite2p.pbs""" % (fps)
print(job_string)
call([job_string],shell=True)
