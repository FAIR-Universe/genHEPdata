#!/bin/bash

cd $DELPHES_DIR

SEED=$1
PROCESS=$2
rm -rf $WorkDir/pythia_$PROCESS_$SEED.root
echo "Random:seed = $SEED" | cat - $WorkDir/share/config_$PROCESS.cmnd > $OutputDir/configBkp/config_$PROCESS-$SEED.cmnd
head $OutputDir/configBkp/config_$PROCESS-$SEED.cmnd
$DELPHES_DIR/DelphesPythia8 $WorkDir/cards/delphes_card_ATLAS_modify.tcl $OutputDir/configBkp/config_$PROCESS-$SEED.cmnd $OutputDir/root_files/pythia_$PROCESS'_'$SEED.root

echo "Waiting for processes to finish...."
wait
echo "Done...."

cd $WorkDir
