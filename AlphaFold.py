from subprocess import call
import time
import glob
import os
import sys

FASTA_file=str(sys.argv[1])

#Create the job file

with open('alphaFold_'+FASTA_file+'.sh','w') as the_file:
    the_file.write('#!/bin/bash \n')
    the_file.write('#SBATCH -N 1 \n')
    the_file.write('#SBATCH --job-name=GillesV_alphafold \n')
    the_file.write('#SBATCH -n 2 \n')
    the_file.write('#SBATCH -c 1 \n')
    the_file.write('#SBATCH --mem=50000 \n')	
    the_file.write('#SBATCH -c 1 \n')
    the_file.write('#SBATCH -o Alpha_out'+FASTA_file+'.txt \n')
    the_file.write('#SBATCH -e Alpha_error'+FASTA_file+'.txt \n')
    the_file.write('#SBATCH --partition=gpu \n')
    the_file.write('#SBATCH --gres=gpu:tesla:1 \n')
    the_file.write('module load singularity; LD_PRELOAD= XDG_RUNTIME_DIR=/tmp/runtime-$USER \n')
    #the_file.write('srun -c 1 -n 2 -N 1 --mem=50000 --gres=gpu:1 --pty /bin/bash singularity exec /scratch/cvl-admin/containers/alphafold.simg ~/exec.sh \n')
    the_file.write('singularity exec /scratch/cvl-admin/containers/alphafold.simg ~/exec.sh \n')
    with open('exec.sh','w') as the_script:
        the_script.write('ldconfig -C /tmp/$USER-ldconfig-cache \n')
        the_script.write('export LD_LIBRARY_PATH=/usr/local/cuda/lib64:/usr/local/cuda/compat:$LD_LIBRARY_PATH \n')
        the_script.write('cd /scratch/sbms/uqgvanwa/alphafold/ \n')
        job_string = 'python ./run_alphafold.py --bfd_database_path /scratch/alphafold/databases/bfd/bfd_metaclust_clu_complete_id30_c90_final_seq.sorted_opt --mgnify_database_path /scratch/alphafold/databases/mgnify/mgy_clusters_2018_12.fa --pdb70_database_path /scratch/alphafold/databases/pdb70/pdb70 --template_mmcif_dir /scratch/alphafold/databases/pdb_mmcif/mmcif_files --obsolete_pdbs_path /scratch/alphafold/databases/pdb_mmcif/obsolete.dat --uniclust30_database_path /scratch/alphafold/databases/uniclust30/uniclust30_2018_08/uniclust30_2018_08 --uniref90_database_path /scratch/alphafold/databases/uniref90/uniref90.fasta --data_dir /scratch/alphafold/databases --max_template_date 2021-08-05 --preset casp14 --model_names model_1_ptm,model_2_ptm,model_3_ptm,model_4_ptm,model_5_ptm --fasta_paths ./'+FASTA_file+'.fasta --output_dir /scratch/sbms/uqgvanwa/AlphaResults/'+FASTA_file+' \n'
        the_script.write(job_string)
        the_script.write('exit \n')
        the_script.write('exit \n')
    os.chmod('exec.sh',0o777)

#Now do some things
job_string = 'sbatch '+'alphaFold_'+FASTA_file+'.sh'
print(job_string)
call([job_string],shell=True)


