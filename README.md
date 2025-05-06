# genHEPdata

This is repository contains the scripts to use for generating HEP sample data with Pythia 8 and Delphes

* The cmnd file for each  process is available in the `share` directory
* The neccesary scripts for generating data is in scripts directory

To generate data use
Step 1.
```
git clone https://github.com/FAIR-Universe/genHEPdata.git
cd genHEPdata/scripts
```
set the ENV variablea correctly. 
```
export DELPHES_DIR=/path/to/delphes
bash ./run_generate.sh <seed> <process> <label>
```

for example `seed` could be 26 and process could be ztautau and hence label will be 0 since its background

The Repository also contains a Docker file which can help you create the neccesary docker image, If running with the image in docker,podman, singularity etc the `DELPHES_DIR` varibale is already assigned.

Example for podman
```
podman run -it \
    -v $WorkDir:/program \
    -e WorkDir=/program \
    docker.io/ragansu/root-delphes:pythia_pip_new bash /program/scripts/run_generator.sh ${seed} ${process} ${label} 
```

Example for Docker
```
docker run -it \
    -v $WorkDir:/program \
    -e WorkDir=/program \
    ragansu/root-delphes:pythia_pip_new bash /program/scripts/run_generator.sh ${seed} ${process} ${label} 
```
Example for singularity
```
singularity exec --bind $WorkDir:/program \
    -e WorkDir=/program \
    docker://ragansu/root-delphes:pythia_pip_new bash /program/scripts/run_generator.sh ${seed} ${process} ${label} 
```



Each job will generate the number of events set in the cmnd files. To increase the numbers one can modify the cmnd files. But an better way would be send parallel jobs by setting approprate seeds. and example of this can be found in `genHEPdata/scripts/run_batch.sh`. Here it is parallised with srun. 



