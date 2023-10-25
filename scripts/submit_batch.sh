#!/bin/bash

PROCESS=$1

for i in {1..10}
do
   echo "Generating $PROCESS Events. ======>  SEED =  $i "
   sbatch run_batch.sh $i $PROCESS
done