#!/bin/bash
#SBATCH --image=rootproject/root:latest
#SBATCH --account=m4287
#SBATCH --qos=regular
#SBATCH -N 1
#SBATCH --constraint=cpu
#SBATCH -t 4:00:00
#SBATCH -J pythia_gen

main_seed=$1
process=$2
label=$3
export WorkDir=/global/cfs/cdirs/m4287/hep/genHEPdata

srun -n 100 -c 2 bash -c "
    seed=\$((${main_seed}*100 + \$SLURM_PROCID))
    $WorkDir/scripts/run_generator.sh \${seed} ${process} ${label}
"
