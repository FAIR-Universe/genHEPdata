#!/bin/bash
#SBATCH --image=rootproject/root:6.28.04-ubuntu22.04
#SBATCH --account=m4287
#SBATCH --qos=shared
#SBATCH --tasks-per-node=1
#SBATCH --constraint=cpu
#SBATCH -t 4:00:00
#SBATCH -J Final_touches


now=$(date +"%Y%m%d")

working_dir=/global/cfs/cdirs/m4287/hep
merged_dir=$working_dir/Delphes_PYTHIA8_output/Merged_files
output_dir=$working_dir/Delphes_PYTHIA8_output/Full_data_files_$now



for Process in ttbar htautau diboson ztautau
do
    {
        
        input_dir=$working_dir/Delphes_PYTHIA8_output/csv_files_$Process
        # Pattern to match the ROOT files (e.g., *.root)
        FILES="$input_dir/*.root"
        
        # Output directory for the merged files
        OUTPUT_DIR="$input_dir/merged_files"
        mkdir -p "$OUTPUT_DIR"
        
        # Number of files to merge per batch
        BATCH_SIZE=1000
        
        # Initialize the batch counter
        batch_num=1
        
        # Loop over the files in batches of BATCH_SIZE
        for ((i = 0; i < $(ls -1 $FILES | wc -l); i += BATCH_SIZE)); do
            # Create a list of files for the current batch
            file_list=$(ls -1 $FILES | sed -n "$((i + 1)),$((i + BATCH_SIZE))p")
            
            # Create the output file name for the current batch
            output_file="$OUTPUT_DIR/merged_${batch_num}.root"
            
            # Run hadd to merge the current batch of files
            shifter --image=rootproject/root:6.28.04-ubuntu22.04 hadd -f "$output_file" $file_list
            
            # Increment the batch counter
            batch_num=$((batch_num + 1))
        done
        
        rm $input_dir/$Process.root
        shifter --image=rootproject/root:6.28.04-ubuntu22.04 hadd ${input_dir}/${Process}.root "$OUTPUT_DIR/merged_*.root"
        
        # This script will merge the csv files generated by the FullDataGenerator into a single file.
        shifter --image=nersc/fair_universe:1298f0a8 python3 $working_dir/genHEPdata/scripts/Data_merger.py --input $input_dir --output $merged_dir/$Process -p
        
        shifter --image=rootproject/root:6.28.04-ubuntu22.04 python $working_dir/genHEPdata/scripts/process_counter.py $input_dir $merged_dir $Process
        
    }
done

shifter --image=nersc/fair_universe:1298f0a8 python3 Final_touches.py \
--input $merged_dir \
--output $output_dir \
--input-format "parquet" \
--output-format "parquet" \
--derived-quantities \
--test-factor 10 \
--public-train-factor 34 \
--public-test-factor 5