#!/bin/bash

# define the paths
export OutputDir="$WorkDir/Output"

mkdir -p $OutputDir
mkdir -p $OutputDir/configBkp
mkdir -p $OutputDir/root_files


sh $WorkDir/scripts/generate_events.sh $1 $2
output_files=$OutputDir/processed_files

if [ ! -d $output_files ]; then
    mkdir $output_files
fi

cd $DELPHES_DIR

root -l -b -q "$WorkDir/scripts/preProcess.cpp(\"$OutputDir/root_files/pythia_${2}_${1}.root\", \"$output_files/process_${1}\", $3, \"$2\")"


# rm -rf $OutputDir/root_files/pythia_$2"_"$1.root
echo "Done at $(date)"
