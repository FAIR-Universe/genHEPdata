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

shifter --image=rootproject/root:latest /bin/bash generate_events.sh $1 $2

# source generate_events.sh $1 $2