#!/bin/bash

PROCESS=$1
Label=$2

export WorkDir=/global/cfs/cdirs/m4287/hep/genHEPdata

for i in {1..100}
do
   echo "Generating $PROCESS Events. ======>  SEED =  $i "
   sbatch $WorkDir/scripts/run_batch.sh $i $PROCESS $Label
done