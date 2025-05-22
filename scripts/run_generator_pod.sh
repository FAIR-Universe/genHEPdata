#!/bin/bash

args=("$@")

seed=${args[0]}
process=${args[1]}
label=${args[2]}

echo $WorkDir

podman-hpc run -it \
    -v $WorkDir:/program \
    -e WorkDir=/program \
    docker.io/ragansu/root-delphes:pythia bash /program/scripts/run_generator.sh ${seed} ${process} ${label} 

echo "Generator finished"