from subprocess import call 
import glob 
import os
import sys

fnames_all =[] 

base_folder='/QRISdata/Q0291/ForANTS/Lactation/' # folder containing the demo files 
for file in glob.glob(os.path.join(base_folder,'*.nrrd')):
    if file.endswith(".nrrd"):
        fnames_all.append(file) 
fnames_all.sort()

for i,name in enumerate(fnames_all):
	#Create the job array
	with open('ANTS_Array.pbs','w') as the_file:
		the_file.write('#!/bin/bash \n')
		the_file.write('#PBS -A UQ-SCI-SBMS \n')
		the_file.write('#PBS -l select=1:ncpus=16:mem=60GB:vmem=60GB \n')
		the_file.write('#PBS -l walltime=12:00:00 \n')
		the_file.write('#PBS -j oe \n')
		output_name = name.replace('.nrrd','_LongReg.nii')
		template_name = "Slice"+str(i+2)+"_Piece_5_template.nii.gz"
		job_string = "antsRegistration -d 3 --float 1 -o [OutImg, OutImg.nii] -n WelchWindowedSinc --winsorize-image-intensities [0.005,0.995] --use-histogram-matching 0 -r [FixImg,MovImg, 1] -t rigid[0.1] -m MI[FixImg,MovImg,1,32, Regular,0.25] -c [1000x500x500x200,1e-8,10] --shrink-factors 8x4x2x1 --smoothing-sigmas 2x1x1x0vox -t Affine[0.1] -m MI[FixImg,MovImg,1,32, Regular,0.25] -c [1000x500x500x200,1e-8,10] --shrink-factors 8x4x2x1 --smoothing-sigmas 2x1x1x0vox -t SyN[0.05,6,0.5] -m CC[FixImg,MovImg,1,2] -c [1000x500x500x500x200,1e-7,10] --shrink-factors 12x8x4x2x1 --smoothing-sigmas 4x3x2x1x0vox -v 1 --restrict-deformation 1x1x0"
		job_string = job_string.replace('OutImg',output_name).replace('FixImg',template_name).replace('MovImg',name)
		the_file.write(job_string)	
	job_string = """qsub ANTS_Array.pbs"""
	call([job_string],shell=True)
	print job_string
