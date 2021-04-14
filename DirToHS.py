from subprocess import call 
import os 
import sys 
dir=str(sys.argv[1])

#Create the job
with open('Fiji.pbs','w') as the_file:
    the_file.write('#!/bin/bash \n')
    the_file.write('#PBS -A UQ-SCI-SBMS \n')
    the_file.write('#PBS -l select=1:ncpus=4:mem=100GB:vmem=100GB \n')
    the_file.write('#PBS -l walltime=8:00:00 \n')
    the_file.write('#PBS -j oe \n')
    #job_string='find '+dir+' -type f -name "*.tif" | xargs recall_medici'
    job_string='''~/Fiji/ImageJ-linux64 --ij2 --headless --console --run DirToHStoSlices.ijm 'myDir="'''+dir+'''"' '''
    #job_string = """ ~/Fiji/ImageJ-linux64 --ij2 --headless --console --run DirToHS.ijm 'myDir=\""""+dir+""""\"' """
    print  job_string
    the_file.write(job_string) 
job_string = """qsub Fiji.pbs""" 
call([job_string],shell=True) 
