#!/bin/bash

LIMIT=300

function checkDelay() {
  eval user=$1
  echo "Check delay of user ${user}..."
  while [ `qstat -u "${user}" | grep "${user}" | wc -l` -gt $LIMIT ]; do
    sleep 10s
  done
}

function runReplicates() {
  eval user=${1}
  eval folder=${2}
  eval binName=${3}
  eval location=${4}
  eval population=${5}
  eval beta=${6}
  eval therapyId=${7}
  eval prmcSize=${8}
  eval ifRate=${9}
  eval startYear=${10}
  eval endYear=${11}
  eval replicates=${12}
  eval tag="${13}_${binName}_${location}_${population}_${beta}_${therapyId}_${prmcSize}_${ifRate}_${startYear}_${endYear}"

  mkdir -p "$HOME/Simulations/Results/${tag}"
  echo "Created folder ${tag} in $HOME/Simulations/Results/"
  sleep 1

  mkdir -p "$HOME/Simulations/Results/${tag}/config"
  echo "Created folder config in $HOME/Simulations/Results/${tag}/"
  sleep 1

  mkdir -p "$HOME/Simulations/Results/${tag}/log"
  echo "Created folder log in $HOME/Simulations/Results/${tag}/"
  sleep 1

  mkdir -p "$HOME/Simulations/Results/${tag}/output"
  echo "Created folder output in $HOME/Simulations/Results/${tag}/"
  sleep 1

  for (( i=1; i<=$replicates; i++ ))
  do

    #
    #YML
    #

    cp  $HOME/Simulations/Scripts/${folder}/templates/sim_prmc.yml $HOME/Simulations/Results/${tag}/config/sim_prmc_${tag}_${i}.yml
    echo "Copy $HOME/Simulations/Scripts/${folder}/templates/sim_prmc.yml to $HOME/Simulations/Results/${tag}/config/sim_prmc_${tag}_${i}.yml"
    sleep 1

    sed -i 's/#POPULATION#/'"${population}"'/g' $HOME/Simulations/Results/${tag}/config/sim_prmc_${tag}_${i}.yml
    echo "Edit POPULATION in $HOME/Simulations/Results/${tag}/config/sim_prmc_${tag}_${i}.yml"
    sleep 1

    sed -i 's/#BETA#/'"${beta}"'/g' $HOME/Simulations/Results/${tag}/config/sim_prmc_${tag}_${i}.yml
    echo "Edit BETA in $HOME/Simulations/Results/${tag}/config/sim_prmc_${tag}_${i}.yml"
    sleep 1

    sed -i 's/#IFR#/'"${ifRate}"'/g' $HOME/Simulations/Results/${tag}/config/sim_prmc_${tag}_${i}.yml
    echo "Edit IFR in $HOME/Simulations/Results/${tag}/config/sim_prmc_${tag}_${i}.yml"
    sleep 1

    sed -i 's/#THERAPYID#/'"${therapyId}"'/g' $HOME/Simulations/Results/${tag}/config/sim_prmc_${tag}_${i}.yml
    echo "Edit THERAPYID in $HOME/Simulations/Results/${tag}/config/sim_prmc_${tag}_${i}.yml"
    sleep 1

    sed -i 's/#PRMCSIZE#/'"${prmcSize}"'/g' $HOME/Simulations/Results/${tag}/config/sim_prmc_${tag}_${i}.yml
    echo "Edit PRMCSIZE in $HOME/Simulations/Results/${tag}/config/sim_prmc_${tag}_${i}.yml"
    sleep 1

    sed -i 's/#STARTYEAR#/'"${startYear}"'/g' $HOME/Simulations/Results/${tag}/config/sim_prmc_${tag}_${i}.yml
    echo "Edit STARTYEAR in $HOME/Simulations/Results/${tag}/config/sim_prmc_${tag}_${i}.yml"
    sleep 1

    sed -i 's/#ENDYEAR#/'"${endYear}"'/g' $HOME/Simulations/Results/${tag}/config/sim_prmc_${tag}_${i}.yml
    echo "Edit ENDYEAR in $HOME/Simulations/Results/${tag}/config/sim_prmc_${tag}_${i}.yml"
    sleep 1

    #
    #PBS
    #

    cp $HOME/Simulations/Scripts/${folder}/templates/run_prmc.pbs $HOME/Simulations/Results/${tag}/log/run_prmc_${tag}_${i}.pbs
    echo "Copy $HOME/Simulations/Scripts/${folder}/templates/run_prmc.pbs to $HOME/Simulations/Results/${tag}/log/run_prmc_${tag}_${i}.pbs"
    dos2unix $HOME/Simulations/Results/${tag}/log/run_prmc_${tag}_${i}.pbs
    sleep 1

    sed -i 's/#TAG#/'"${tag}"'/g' $HOME/Simulations/Results/${tag}/log/run_prmc_${tag}_${i}.pbs
    echo "Edit TAG in $HOME/Simulations/Results/${tag}/log/run_prmc_${tag}_${i}.pbs"
    sleep 1

  done

  cd $HOME/Simulations/Results/${tag}/log
  echo "cd $HOME/Simulations/Results/${tag}/log"

  for (( i=1; i<=$replicates; i++ ))
  do
    checkDelay ${user}
    qsub -F "${binName} ${tag} ${i}" run_prmc_${tag}_${i}.pbs
    echo "qsub -F "${binName} ${tag} ${i}" run_prmc_${tag}_${i}.pbs"
  done

  cd $HOME/Simulations/
  echo "Scheduled all simulations, back to $HOME/Simulations folder"
}