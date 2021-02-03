from subprocess import call 
import glob 
import os
import sys

fnames_all =[] 
folder=str(sys.argv[1])
#FixedImg=str(sys.argv[2])

base_folder='/QRISdata/Q0291/ForANTS/'+folder+'/' # folder containing the demo files 
for file in glob.glob(os.path.join(base_folder,'hs*.nrrd')):
    if file.endswith(".nrrd"):
        fnames_all.append(file) 
fnames_all.sort()
#FixedImg=base_folder+FixedImg

for i,name in enumerate(fnames_all):
	#Create the job array		
	fixed_file=name.replace('hs_','AVG_EMLLDC_loomhab_')
	fixed_file=fixed_file.replace('.nrrd','_1_2Hz_SL50_TP750_HD_range240_step1_exposure100_power80.nrrd')
	#job_string = """antsRegistration -d 3 --float 1 -o ["""+output_name+""", """+output_name+""".nii] -n WelchWindowedSinc --winsorize-image-intensities [0.01,0.99] --use-histogram-matching 1 -r ["""+FixedImg+""".nrrd,"""+name+""", 1] -t rigid[0.1] -m MI["""+FixedImg+""".nrrd,"""+name+""",1,32, Regular,0.5] -c [1000x500x500x500,1e-8,10] --shrink-factors 8x4x2x1 --smoothing-sigmas 2x1x1x0vox -t Affine[0.1] -m MI["""+FixedImg+""".nrrd,"""+name+""",1,32, Regular,0.5] -c [1000x500x500x500,1e-8,10] --shrink-factors 8x4x2x1 --smoothing-sigmas 2x1x1x0vox -t SyN[0.05,6,0.5] -m CC["""+FixedImg+""".nrrd,"""+name+""",1,2] -c [1000x500x500x500x500,1e-7,10] --shrink-factors 12x8x4x2x1 --smoothing-sigmas 4x3x2x1x0vox -v 0 \n"""
	job_string = """antsRegistrationSyNQuick.sh -d 3 -f """+fixed_file+""" -m """+name+""" -o QuickReg -p f -j 1 \n"""
	print job_string
	call([job_string],shell=True)	
