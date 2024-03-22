#!/bin/bash
#SBATCH --image=rootproject/root:latest
#SBATCH --account=atlas
#SBATCH --qos=shared
#SBATCH --tasks-per-node=1
#SBATCH --constraint=cpu
#SBATCH -t 4:00:00
#SBATCH -J pythia_gen

module load python
# export PYTHIA8=/global/cfs/projectdirs/atlas/elham/Pythia8
export OutputDir=/global/cfs/projectdirs/atlas/elham/fair_universe_simulation/higgs_extrabkgs/

shifter --image=rootproject/root:latest /bin/bash generate_events.sh $1 $2
cd /global/cfs/projectdirs/atlas/elham/Delphes-3.5.0/
shifter --image=rootproject/root:latest root -l /global/cfs/projectdirs/atlas/elham/fair_universe_simulation/Fair_Universe_Delphes/src/preProcess.C\(\"$OutputDir/pythia_$2"_"$1.root\",\"$OutputDir/hist_$2"_"$1\",0,200000,1\)

# source generate_events.sh $1 $2