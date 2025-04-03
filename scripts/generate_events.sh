#!/bin/bash

export PYTHIA8=/global/cfs/cdirs/m4287/hep/Pythia8

# define the paths
export Delphes_Path=/global/cfs/cdirs/m4287/hep/Delphes-3.5.0
export WorkDir=/global/cfs/cdirs/m4287/hep/genHEPdata
export OutputDir=/global/cfs/cdirs/m4287/hep/DATA_PHASE_2

cd $Delphes_Path


SEED=$1
PROCESS=$2
rm -rf $WorkDir/pythia_$PROCESS_$SEED.root
echo "Random:seed = $SEED" | cat - $WorkDir/share/config_$PROCESS.cmnd > $OutputDir/configBkp/config_$PROCESS-$SEED.cmnd
head $OutputDir/configBkp/config_$PROCESS-$SEED.cmnd
$Delphes_Path/DelphesPythia8 $WorkDir/cards/delphes_card_ATLAS_modify.tcl $OutputDir/configBkp/config_$PROCESS-$SEED.cmnd $OutputDir/root_files/pythia_$PROCESS'_'$SEED.root

echo "Waiting for processes to finish...."
wait
echo "Done...."

cd $WorkDir
