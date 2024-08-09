#!/bin/bash
#SBATCH --image=rootproject/root:6.28.04-ubuntu22.04
#SBATCH --account=m4287
#SBATCH --qos=shared
#SBATCH --tasks-per-node=1
#SBATCH --constraint=cpu
#SBATCH -t 4:00:00
#SBATCH -J pythia_gen$2

module load python
# export PYTHIA8=/global/cfs/cdirs/m4287/hep//Pythia8
export OutputDir=/global/cfs/cdirs/m4287/hep/Delphes_PYTHIA8_output
export WorkDir=/global/cfs/cdirs/m4287/hep/genHEPdata

shifter --image=rootproject/root:6.28.04-ubuntu22.04 /bin/bash $WorkDir/scripts/generate_events.sh $1 $2
cd /global/cfs/cdirs/m4287/hep/Delphes-3.5.0
csv_files=$OutputDir/csv_files_$2

if [ ! -d $csv_files ]; then
    mkdir $csv_files
fi

shifter --image=rootproject/root:6.28.04-ubuntu22.04 root -l $WorkDir/scripts/preProcess.cpp\(\"$OutputDir/root_files/pythia_$2"_"$1.root\",\"$csv_files/hist_$2"_"$1\",$3\)

# source generate_events.sh $1 $2
