#!/bin/bash
export OutputDir=/global/cfs/cdirs/m4287/hep/DATA_PHASE_2
export WorkDir=/global/cfs/cdirs/m4287/hep/genHEPdata

sh $WorkDir/scripts/generate_events.sh $1 $2
cd /global/cfs/cdirs/m4287/hep/Delphes-3.5.0
csv_files=$OutputDir/csv_files_$2

if [ ! -d $csv_files ]; then
    mkdir $csv_files
fi

root -l -b -q  $WorkDir/scripts/preProcess.cpp\(\"$OutputDir/root_files/pythia_$2"_"$1.root\",\"$csv_files/hist_$2"_"$1\",$3\)

rm -rf $OutputDir/root_files/pythia_$2"_"$1.root
echo "Done at $(date)"
