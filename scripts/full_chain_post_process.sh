#!/bin/bash
#SBATCH --image=ragansu/fair-universe-data:test
#SBATCH --account=dasrepo
#SBATCH --qos=regular
#SBATCH -N 1
#SBATCH --constraint=cpu
#SBATCH -t 4:00:00
#SBATCH -J Final_touches

now=$(date +"%Y%m%d")


# Set default values for the optional arguments
public_train_factor=100
public_test_factor=60
test_factor=60
luminocity=10 # in fb^-1

# Define the working directory

working_dir=/global/cfs/cdirs/m4287/hep
WorkDir=$working_dir/genHEPdata
data_dir=$working_dir/NEW_DelphesPythia_data
merged_dir=$data_dir/Merged_files
output_dir=$data_dir/Full_data_files_$now

Processes=("ttbar" "ztautau" "htautau" "diboson")

# Use srun to execute the script with Shifter
srun -n 4 -c 256 shifter bash -c "
    # Define the array inside the shifter environment
    Processes=('ttbar' 'ztautau' 'htautau' 'diboson')

    # Access the correct process based on SLURM_PROCID
    process=\${Processes[\$SLURM_PROCID]}
    input_dir=${data_dir}/csv_files_\${process}
    # Run the test script with the appropriate arguments
    $WorkDir/scripts/run_merger.sh \${process} \${input_dir} ${merged_dir}
"

wait

echo "All jobs are done!"

# Merge the merged files into a single file
echo
echo "Merging the merged files into a single file"
echo
echo "Final touches"

srun -n 1 -c 256 shifter python3  ${WorkDir}/scripts/Final_touches.py --input ${merged_dir} --output ${output_dir} --input-format "parquet" --output-format "parquet" --test-factor ${test_factor} --public-train-factor ${public_train_factor} --public-test-factor ${public_test_factor} --luminocity ${luminocity}
