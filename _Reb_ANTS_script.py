from subprocess import call 
import glob 
import os
import sys

fnames_all =[] 
folder=str(sys.argv[1])
FixedImg=str(sys.argv[2])

base_folder='/QRISdata/Q0291/ForANTS/'+folder+'/' # folder containing the demo files 
for file in glob.glob(os.path.join(base_folder,'RebeccaGoodFishTemplatetemplate0.nii.gz')):
	fnames_all.append(file) 
fnames_all.sort()
FixedImg=base_folder+FixedImg

for i,name in enumerate(fnames_all):
	#Create the job array
	with open('ANTS_Array.pbs','w') as the_file:
		the_file.write('#!/bin/bash \n')
		the_file.write('#PBS -A UQ-SCI-SBMS \n')
		the_file.write('#PBS -l select=1:ncpus=16:mem=300GB:vmem=300GB \n')
		the_file.write('#PBS -l walltime=48:00:00 \n')
		the_file.write('#PBS -j oe \n')
		output_name=name.replace('.nii.gz','To'+FixedImg.replace(base_folder,''))		
		job_string = """antsRegistration -d 3 --float 1 -o ["""+output_name+""", """+output_name+""".nii] -n WelchWindowedSinc --winsorize-image-intensities [0.005,0.995] --use-histogram-matching 0 -r ["""+FixedImg+""".nrrd,"""+name+""", 1] -t rigid[0.1] -m MI["""+FixedImg+""".nrrd,"""+name+""",1,32, Regular,0.25] -c [1000x500x500x200,1e-8,10] --shrink-factors 8x4x2x1 --smoothing-sigmas 2x1x1x0vox -t Affine[0.1] -m MI["""+FixedImg+""".nrrd,"""+name+""",1,32, Regular,0.25] -c [1000x500x500x200,1e-8,10] --shrink-factors 8x4x2x1 --smoothing-sigmas 2x1x1x0vox -t SyN[0.05,6,0.5] -m CC["""+FixedImg+""".nrrd,"""+name+""",1,2] -c [1000x500x500x500x200,1e-7,10] --shrink-factors 12x8x4x2x1 --smoothing-sigmas 4x3x2x1x0vox -v 0 \n"""
		the_file.write(job_string)	
	job_string = """qsub ANTS_Array.pbs"""
	call([job_string],shell=True)
	print job_string
