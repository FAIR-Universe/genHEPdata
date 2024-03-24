#!/bin/bash
module load python
shifter --image=rootproject/root:latest /bin/bash
export PYTHIA8=/global/cfs/cdirs/m4287/hep/Pythia8

# define the paths
export Delphes_Path=/global/cfs/cdirs/m4287/hep/Delphes-3.5.0/
export WorkDir=/global/cfs/cdirs/m4287/hep/fair_universe_simulation/

cd $Delphes_Path


SEED=$1
PROCESS=$2
rm -rf $WorkDir/pythia_$PROCESS_$SEED.root
echo "Random:seed = $SEED" | cat - $WorkDir/config_$PROCESS.cmnd > $WorkDir/configBkp/config_$PROCESS-$SEED.cmnd
head $WorkDir/configBkp/config_$PROCESS-$SEED.cmnd
./DelphesPythia8 $WorkDir/cards/delphes_card_ATLAS_updated.tcl $WorkDir/configBkp/config_$PROCESS-$SEED.cmnd $WorkDir/pythia_$PROCESS'_'$SEED.root


echo "Waiting for processes to finish...."
wait
echo "Done...."

cd $WorkDir