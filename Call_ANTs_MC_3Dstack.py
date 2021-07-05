from subprocess import call
import time
import glob
import os
import sys

fnames_all =[]
folder=str(sys.argv[1])
base_folder='/QRISdata/'+folder # folder containing the demo files
for file in glob.glob(os.path.join(base_folder,'GV*/')):    
    fnames_all.append(file)
fnames_all.sort()

#Create the job array

with open('ENS_3D.pbs','w') as the_file:
	the_file.write('#!/bin/bash \n')
	the_file.write('#PBS -A UQ-SCI-SBMS \n')
	the_file.write('#PBS -l select=1:ncpus=18:mem=120GB:vmem=120GB \n')
	the_file.write('#PBS -l walltime=100:00:00 \n')
	the_file.write('#PBS -j oe \n')
	job_string = """#PBS -t 1-%s \n""" % (str(len(fnames_all)))
	the_file.write(job_string)
	job_string = 'filename=`ls -d '+base_folder+'/GV_* | tail -n +\${PBS_ARRAY_INDEX} | head -1` \n'
	the_file.write(job_string)
	#the_file.write('/usr/local/bin/recall_medici $filename \n')
	the_file.write(' module load anaconda \n')
	job_string = 'python ~/ANTs_MC_3Dstack.py $filename \n' 
	the_file.write(job_string)

#Now do some things
job_string = """qsub ENS_3D.pbs"""
#print job_string
call([job_string],shell=True)
