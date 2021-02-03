from subprocess import call
import time
import glob
import os
import sys

fnames_all =[]
folder=str(sys.argv[1])
fps=str(sys.argv[2])
#comp=str(sys.argv[3])
base_folder='/QRISdata/Q0291/ForANTS/'+folder # folder containing the demo files
for file in glob.glob(os.path.join(base_folder,'*.nrrd')):
    if file.endswith(".nrrd"):
        fnames_all .append(file)
fnames_all.sort()

#Create the job array
with open('ANTS_Array.pbs','w') as the_file:
	the_file.write('#!/bin/bash \n')
	the_file.write('#PBS -A UQ-SCI-SBMS \n')
	the_file.write('#PBS -l select=1:ncpus=6:mem=150GB:vmem=150GB \n')
	the_file.write('#PBS -l walltime=24:00:00 \n')
	the_file.write('#PBS -j oe \n')
	job_string = """#PBS -t 1-%s \n""" % (str(len(fnames_all)))
	the_file.write(job_string)
	job_string = 'filename=`ls -1 '+base_folder+'/*.nrrd | tail -n +\${PBS_ARRAY_INDEX} | head -1` \n'
	the_file.write(job_string)
	job_string = 'output=$filename;output+=\'_long\''
	the_file.write(job_string)
	job_string = """antsRegistration -d 3 --float 1 -o [$output, $output.nii] -n WelchWindowedSinc --winsorize-image-intensities [0.005,0.995] --use-histogram-matching 0 -r [$FPS,$filename, 1] -t rigid[0.1] -m MI[$FPS,$filename,1,32, Regular,0.25] -c [1000x500x500x200,1e-8,10] --shrink-factors 8x4x2x1 --smoothing-sigmas 2x1x1x0vox -t Affine[0.1] -m MI[$FPS,$filename,1,32, Regular,0.25] -c [1000x500x500x200,1e-8,10] --shrink-factors 8x4x2x1 --smoothing-sigmas 2x1x1x0vox -t SyN[0.05,6,0.5] -m CC[$FPS,$filename,1,2] -c [1000x500x500x500x200,1e-7,10] --shrink-factors 12x8x4x2x1 --smoothing-sigmas 4x3x2x1x0vox -v 0 \n"""
	the_file.write(job_string)

#Now do some things
os.environ["FPS"]=fps
os.environ["COMP"]="_long"
job_string = """qsub -v FPS=%s ANTS_Array.pbs""" % (fps)
#job_string = """qsub -v FPS=%s,COMP=%s ANTS_Array.pbs""" % (fps, comp)
print job_string
call([job_string],shell=True)

