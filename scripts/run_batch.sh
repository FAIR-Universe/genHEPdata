#!/bin/bash
#SBATCH --image=rootproject/root:6.28.04-ubuntu22.04 
#SBATCH --account=m4287
#SBATCH --qos=regular
#SBATCH -N 1
#SBATCH --constraint=cpu
#SBATCH -t 4:00:00
#SBATCH -J pythia_gen


number_of_jobs=$(($SLURM_NNODES*128)) # Number of jobs to run set to 128 per node
main_seed=0
process=ztautau
label=0

echo
echo "Start"
echo "Date and Time      : $now"
echo "SLURM_JOB_ID       : $SLURM_JOB_ID"
echo "SLURM_JOB_NODELIST : $SLURM_JOB_NODELIST"
echo "SLURM_NNODES       : $SLURM_NNODES"
echo "Number of jobs     : $number_of_jobs"
echo "Main seed          : $main_seed"
echo "Process            : $process"
echo "Label              : $label"
echo

module load python

export WorkDir= # replace with the actual path to your working directory

srun -n $number_of_jobs -c 2 shifter bash -c "
    seed=\$((${main_seed} + \$SLURM_PROCID))
    ${WorkDir}/scripts/run_generator.sh \${seed} ${process} ${label}
"

wait
echo "All jobs are done!"