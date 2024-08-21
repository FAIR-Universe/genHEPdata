#!/bin/bash
#SBATCH --image=ragansu/fair-universe-data:test
#SBATCH --account=m4287
#SBATCH --qos=regular
#SBATCH -N 1
#SBATCH --constraint=cpu
#SBATCH -t 4:00:00
#SBATCH -J Final_touches

now=$(date +"%Y%m%d")

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        -p|--public-train-factor)
            public_train_factor=$2
            shift 2
            ;;
        -t|--public-test-factor)
            public_test_factor=$2
            shift 2
            ;;
        -f|--test-factor)
            test_factor=$2
            shift 2
            ;;
        -l|--luminocity)
            luminocity=$2
            shift 2
            ;;
        *)
            echo "Invalid argument: $1"
            exit 1
            ;;
    esac
done

working_dir=/global/cfs/cdirs/m4287/hep/genHEPdata
data_dir=$working_dir/NEW_DelphesPythia_data
merged_dir=$data_dir/Merged_files
output_dir=$data_dir/Full_data_files_$now

Processes=("ttbar" "ztautau" "htautau" "diboson")

# Use srun to execute the script with Shifter
srun -n 4 -c 64 shifter bash -c "
    # Define the array inside the shifter environment
    Processes=('ttbar' 'ztautau' 'htautau' 'diboson')

    # Access the correct process based on SLURM_PROCID
    process=\${Processes[\$SLURM_PROCID]}
    input_dir=$data_dir/csv_files_$process
    # Run the test script with the appropriate arguments
    $WorkDir/scripts/run_merger.sh \${process} ${input_dir} ${merged_dir}
"

srun -n 1 -c 256 shifter python3  Final_touches.py --input $merged_dir --output $output_dir --input-format "parquet" --output-format "parquet" --test-factor ${test_factor} --public-train-factor ${public_train_factor} --public-test-factor ${public_train_factor} --luminocity ${luminocity}
