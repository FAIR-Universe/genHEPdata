# This script is used to run the merger in a podman container
#!/bin/bash

podman-hpc run -it \
    -v $WorkDir:/program \
    -e WorkDir=/program \
    docker.io/ragansu/root-delphes:pythia_pip_new bash /program/scripts/run_merger.sh > log_file_com.log 2> err_file_com.log 