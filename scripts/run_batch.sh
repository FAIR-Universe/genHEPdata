#!/bin/bash
#SBATCH --image=rootproject/root:6.28.04-ubuntu22.04 
#SBATCH --account=m4287
#SBATCH --qos=regular
#SBATCH -N 1
#SBATCH --constraint=cpu
#SBATCH -t 4:00:00
#SBATCH -J pythia_gen

module load python

main_seed=$1
process=$2
label=$3
export WorkDir=/global/cfs/cdirs/m4287/hep/genHEPdata

srun -n 64 -c 4 rootproject/root:6.28.04-ubuntu22.04 bash -c "
    seed=\$((${main_seed}*64 + \$SLURM_PROCID))
    $WorkDir/scripts/run_generator.sh \${seed} ${process} ${label}
"
