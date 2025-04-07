#!/bin/bash

# define the paths
export OutputDir="$WorkDir/Output"

mkdir -p $OutputDir
mkdir -p $OutputDir/configBkp
mkdir -p $OutputDir/root_files


sh $WorkDir/scripts/generate_events.sh $1 $2
csv_files=$OutputDir/csv_files_$2

if [ ! -d $csv_files ]; then
    mkdir $csv_files
fi

root -l -b -q  $WorkDir/scripts/preProcess.cpp\(\"$OutputDir/root_files/pythia_$2"_"$1.root\",\"$csv_files/hist_$2"_"$1\",$3\)

rm -rf $OutputDir/root_files/pythia_$2"_"$1.root
echo "Done at $(date)"
