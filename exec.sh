ldconfig -C /tmp/$USER-ldconfig-cache 
export LD_LIBRARY_PATH=/usr/local/cuda/lib64:/usr/local/cuda/compat:$LD_LIBRARY_PATH 
cd /scratch/sbms/uqgvanwa/alphafold/ 
python ./run_alphafold.py --bfd_database_path /scratch/alphafold/databases/bfd/bfd_metaclust_clu_complete_id30_c90_final_seq.sorted_opt --mgnify_database_path /scratch/alphafold/databases/mgnify/mgy_clusters_2018_12.fa --pdb70_database_path /scratch/alphafold/databases/pdb70/pdb70 --template_mmcif_dir /scratch/alphafold/databases/pdb_mmcif/mmcif_files --obsolete_pdbs_path /scratch/alphafold/databases/pdb_mmcif/obsolete.dat --uniclust30_database_path /scratch/alphafold/databases/uniclust30/uniclust30_2018_08/uniclust30_2018_08 --uniref90_database_path /scratch/alphafold/databases/uniref90/uniref90.fasta --data_dir /scratch/alphafold/databases --max_template_date 2021-08-05 --preset casp14 --model_names model_1_ptm,model_2_ptm,model_3_ptm,model_4_ptm,model_5_ptm --fasta_paths ./O14791.fasta --output_dir /scratch/sbms/uqgvanwa/AlphaResults/O14791 
exit 
exit 
