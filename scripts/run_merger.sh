
input_dir=$WorkDir/Output/processed_files
merged_dir=$WorkDir/Output/merged_files
output_file_name=1
default_value="Merged"

output_filename=${1:-default_value}

# Check if the input directory is provided
if [ -z "$input_dir" ]; then
    echo "Usage: $0 <input_directory>"
    exit 1
fi

mkdir -p $merged_dir


# Pattern to match the ROOT files (e.g., *.root)
FILES="$input_dir/process_*.root"

# Output directory for the merged files
OUTPUT_DIR="$input_dir/merged_files"
mkdir -p "$OUTPUT_DIR"

# Number of files to merge per batch
BATCH_SIZE=1000

echo "Merging ROOT files in $input_dir"
echo "Output directory: $OUTPUT_DIR"
echo "Merging files in batches of $BATCH_SIZE"


# Initialize the batch counter
batch_num=1

ls $input_dir 

echo "Files to merge: $FILES"

file_list=$input_dir/file_name_list.txt

ls $FILES > $file_list

# Loop over the files in batches of BATCH_SIZE
cat ${file_list} | xargs -n $BATCH_SIZE | while read -r file_list; do
    # Create the output file name for the current batch
    output_file="$OUTPUT_DIR/merged_${batch_num}.root"
    
    echo "Merging batch $batch_num into $output_file"

    # Run hadd to merge the current batch of files
    hadd -f "$output_file" $file_list
    
    # Increment the batch counter
    batch_num=$((batch_num + 1))
done


rm $input_dir/Merged.root
merged_file_list=$(ls -1 $OUTPUT_DIR/*.root)

hadd ${input_dir}/Merged.root $merged_file_list


python3 $WorkDir/scripts/Final_touches.py --input $input_dir/Merged.root --output $merged_dir/$output_filename -p --luminocity 10
        