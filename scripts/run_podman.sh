#!/bin/bash

args=("$@")

seed=${args[0]}
process=${args[1]}
label=${args[2]}

podman-hpc run -it \
    -v $WorkDir:/program \
    root-delphes/latest  bash /program/scripts/run_generator.sh ${seed} ${process} ${label} 

echo "Generator finished"