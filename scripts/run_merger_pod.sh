
Process=$1
input_dir=$2

podman-hpc run -it \
    -v $WorkDir:/program \
    -e WorkDir=/program \
    docker.io/ragansu/root-delphes:pythia bash /program/scripts/run_merger.sh ${Process} ${input_dir} ${merged_dir}