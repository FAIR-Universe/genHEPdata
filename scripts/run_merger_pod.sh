# This script is used to run the merger in a podman container
#!/bin/bash
input_dir=$1


podman-hpc run -it \
    -v $WorkDir:/program \
    -v $input_dir:/input \
    -e WorkDir=/program \
    docker.io/ragansu/root-delphes:pythia_pip_new python3 /program/scripts/convert_data_format.py --input /input --output /program/Output/merged_files/Phase_1 -p > log_file_com.log 2> err_file_com.log 