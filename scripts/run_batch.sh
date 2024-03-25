#!/bin/bash
#SBATCH --image=rootproject/root:latest
#SBATCH --account=atlas
#SBATCH --qos=shared
#SBATCH --tasks-per-node=1
#SBATCH --constraint=cpu
#SBATCH -t 4:00:00
#SBATCH -J pythia_gen

module load python
# export PYTHIA8=/global/cfs/cdirs/m4287/hep//Pythia8
export OutputDir=/global/cfs/cdirs/m4287/hep/Delphes_PYTHIA8_output/higgs_extrabkgs/

shifter --image=rootproject/root:latest /bin/bash generate_events.sh $1 $2
cd /global/cfs/cdirs/m4287/hep/Delphes-3.5.0/
shifter --image=rootproject/root:latest root -l ./preProcess.C\(\"$OutputDir/pythia_$2"_"$1.root\",\"$OutputDir/hist_$2"_"$1\",0,200000,1\)

# source generate_events.sh $1 $2