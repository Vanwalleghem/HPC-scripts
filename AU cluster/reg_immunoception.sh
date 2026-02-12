#!/bin/bash
# Date : 13/11/2025
# Last Modified : SBF
# reg_ctrl_dss.sh 
# This version registers zebrafish brain images (ctrl and dss) to a standard reference brain.

# Parameter files used for registration
BINDIR="/faststorage/project/Inflammation/BREEZE/bin";
STANDARD_REFERENCE="standard_ref.nii.gz"
STANDARD_RSP_REFERENCE=STANDARD_REFERENCE
NON_PARAM_FILE="nonlinearRegistration.param"
DIS_ATLAS_MASK_FILE="dis_atlas_mask.nii.gz"

# Checks if a certain job is already running
check_jobs() {
if ls logs/${1}.job 1> /dev/null 2>&1; then
	for jobid in $(squeue --me -o "%i" -h)
	do
		if grep ${jobid} logs/${1}.job 1> /dev/null 2>&1; then
			echo "CANNOT RUN - Please try later after current ${1} job is done"
			exit 1
		fi
	done
	rm -f logs/${1}.job
fi
}
# Checks if required files exist
check_files() {
if ! ls ${1} 1> /dev/null 2>&1; then
	echo "ERROR: Cannot access ${1} No such file or folder"
	exit 1
fi
}
# Checks if parameter and reference file exist 
check_string() {
if [ ! -f ${1} ]; then
	echo "ERROR: Cannot access ${1} param/reference file"
	exit 1
fi
}
# Checks if a certain command is available in the environment
check_command() {
if ! command -v ${1} 1> /dev/null 2>&1; then
     echo "ERROR: ${1}: command not found..."
     exit 1
fi
}
# Defines the command to be executed by the SLURM job scheduler
cmd() {
cat << EOF 
#!/bin/bash
#SBATCH --account Inflammation 
#SBATCH --partition normal
#SBATCH -J reg_${file}
#SBATCH --out="logs/reg_${file}.out"
#SBATCH --error="logs/reg_${file}.log"
#SBATCH -c 8
#SBATCH --mem=60G
#SBATCH -t 1-00:00:00
#SBATCH --mail-type=END
#SBATCH --mail-user=${EMAIL}
source ~/miniforge3/etc/profile.d/conda.sh
conda init
conda activate node
# Input variables

input_c0_file="nrrd/${file}_C0.nrrd"
input_c1_file="nrrd/${file}_C1.nrrd"
input_c2_file="nrrd/${file}_C2.nrrd"
bisxform_file="standard_ref__${file}_C1__optfixed__nlr.bisxform"
registered_c0_file="r_${file}_C0.nrrd"
registered_c1_file="r_${file}_C1.nrrd"
registered_c2_file="r_${file}_C2.nrrd"
affine_c0_file="a_${file}_C0.nrrd"
affine_c1_file="a_${file}_C1.nrrd"
affine_c2_file="a_${file}_C2.nrrd"
warp_c0_file="w_${file}_C0.nrrd"
warp_c1_file="w_${file}_C1.nrrd"
warp_c2_file="w_${file}_C2.nrrd"


# Creates registered (C0,C1) and bisxform files

#biswebnode nonlinearregistration --paramfile ${NON_PARAM_FILE} -r ${STANDARD_REFERENCE} -t \${input_c1_file}
greedy -d 3 -a -o ${affine_c1_file} -i ${STANDARD_REFERENCE} ./${input_c1_file}  -n 100x40x20 -ia-image-centers -m MNI
greedy -d 3 -float -o ./${warp_c1_file} -i ${STANDARD_REFERENCE} ./${input_c1_file}  -it ${affine_c1_file} -n 100x50x20 -e 0.25 -m NCC 2x2x2
#biswebnode resliceImage -r ${STANDARD_REFERENCE} -i \${input_c1_file} -x \${bisxform_file} -o \${registered_c1_file}
greedy -d 3 -rf ${STANDARD_REFERENCE} -rm ./${input_c1_file} ./${registered_c1_file} -r ./${warp_c1_file} ${affine_c1_file}
biswebnode resliceImage -r \${registered_c1_file} -i \${input_c0_file} -x \${bisxform_file} -o \${registered_c0_file}
greedy -d 3 -rf ${STANDARD_REFERENCE} -rm ./${input_c0_file} ./${registered_c1_file} -r ./${warp_c1_file} ${affine_c1_file}

# Creates C0divC1 divided files

mkdir -p divided/C0divC1
divided_file="r_${file}_C0divC1.nii.gz"
fslmaths \${registered_c0_file} -div \${registered_c1_file} divided/C0divC1/\${divided_file}

# Creates registered (C2) and bisxform files

if [ -f \${input_c2_file} ]
then
	biswebnode resliceImage -r \${registered_c1_file} -i \${input_c2_file} -x \${bisxform_file} -o \${registered_c2_file}

# Creates C2divC1 divided files

	mkdir -p divided/C2divC1
	divided_file="r_${file}_C2divC1.nii.gz"
	fslmaths \${registered_c2_file} -div \${registered_c1_file} divided/C2divC1/\${divided_file}
fi

# Creates jacobian files (ja_ and mask_ja) for C1 using bisxform files

jacobian_file="ja_${file}.nii.gz"
#mask_file="mask_ja_${file}.nii.gz"
#biswebnode jacobianimage -x \${bisxform_file} -i ${BINDIR}/${STANDARD_RSP_REFERENCE} -o jacobian/\${jacobian_file}
greedy -d 3 -jac ./${warp_c1_file} ./${jacobian_file}
#biswebnode maskimage -i jacobian/\${jacobian_file} -m ${BINDIR}/${DIS_ATLAS_MASK_FILE} -o jacobian/\${mask_file}

# Moves registered files to registered folder

#mv \${bisxform_file} xform
mv \${registered_c1_file} registered
mv \${registered_c0_file} registered
if [ -f \${input_c2_file} ]
then
	mv \${registered_c2_file} registered
fi

EOF
}

# Sets to ignore case in filename (ex. WT and wt will be considered as wildtype)

shopt -s nocaseglob nocasematch

# Checks for required commands

check_command sbatch
check_command biswebnode

# Checks for required files

for geno_type in ctrl dss
do
	check_files "optfixed/*_${geno_type}_*C0.nrrd"
done

# Checks if C1 optfixed file exists in optfixed folder
check_files optfixed/*C1.nrrd

# Checks if registration is running
check_jobs registered

mkdir -p scripts logs

# Checks if reference file exists

check_string ${BINDIR}/${STANDARD_REFERENCE}

# Checks if parameter file exists

check_string ${BINDIR}/${NON_PARAM_FILE}

# Copies reference file and parameter file to current directory for registration
cp ${BINDIR}/${STANDARD_REFERENCE} .
cp ${BINDIR}/${NON_PARAM_FILE} .

# Creates registered, jacobian, xform and divided folders

rm -rf registered jacobian xform divided 
mkdir -p registered jacobian xform divided 
for file in $(cd optfixed 2> /dev/null; ls *0.nrrd)
do
	file=`echo \$file | sed s/_C..nrrd//g`
	cmd | sbatch > scripts/reg_${file}.sh
	cmd | sbatch | tee -a logs/registered.job
done

