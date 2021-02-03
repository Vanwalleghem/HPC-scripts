from subprocess import call 
import glob 
import os
import sys

fnames_all =[] 
base_folder='/30days/uqgvanwa/lactation/' # folder containing the demo files 
for file in glob.glob(os.path.join(base_folder,'C2*.nrrd')):
    if file.endswith(".nrrd"):
        fnames_all.append(file) 
fnames_all.sort()


for i,name in enumerate(fnames_all):
	#Create the job array
	with open('ANTS_Flash.pbs','w') as the_file:
		the_file.write('#!/bin/bash \n')
		the_file.write('#PBS -A UQ-SCI-SBMS \n')
		the_file.write('#PBS -l select=1:ncpus=16:mem=300GB:vmem=300GB \n')
		the_file.write('#PBS -l walltime=24:00:00 \n')
		the_file.write('#PBS -j oe \n')
		output_name=name.replace('.nrrd','ToTemplate.nii')		
		FixedImg=name.replace('.nrrd','_template.nii.gz')
		job_string = "antsRegistration -d 3 --float 1 -o [OutImg, OutImg.nii] -n WelchWindowedSinc -w [0.005,0.995] -u 1 -r [FixImg,MovImg, 1] -t rigid[0.1] -m MI[FixImg,MovImg,1,32, Regular,0.25] -c [1000x500x500x200,1e-8,10] -f 8x4x2x1 -s 2x1x1x0vox -g 1x1x0x1x1x0 -t Affine[0.1] -m MI[FixImg,MovImg,1,32, Regular,0.25] -c [1000x500x500x200,1e-8,10] -f 8x4x2x1 -s 2x1x1x0vox -g 1x1x1x1x1x1x0x0x0x1x1x0 -t SyN[0.05,6,0.5] -m CC[FixImg,MovImg,1,2] -c [500x500x500x200,1e-7,5] -f 8x4x2x1 -s 2x2x1x0vox -v 1 -g 1x1x0"
		job_string = job_string.replace('OutImg',output_name).replace('FixImg',FixedImg).replace('MovImg',name)
		the_file.write(job_string)	
	job_string = """qsub ANTS_Flash.pbs"""
	call([job_string],shell=True)
	print job_string
