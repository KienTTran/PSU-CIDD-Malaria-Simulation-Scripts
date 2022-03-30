#!/bin/bash

LIMIT=300

function help(){
  echo "./Schedule_Run_PRMC_1 {user} {folder} {location} {therapyId} {prmcSize} {ifRate} {replicates} {tag}"
  echo "Arguments:"
  echo " - user: username (string)"
  echo " - folder: name of the Study scripts that has been uploaded to server (string)"
  echo " - location: non-negative integer (1 - inf)"
  echo " - therapyId:  non negative interger (0 - 4)"
  echo " - prmcSize: non negative interger (1 - inf)"
  echo " - ifRate: non negative float (0.1 - 1.0)"
  echo " - replicates: non negative interger (1 - inf)"
  echo " - tag: name of the study, will be created in $HOME/Simulations/ (string)"
  echo "Example:"
  echo "    ./Schedule_Run_PRMC_1 ktt5121 PRMC_1 4 50000 0 100 0.19 5 Tag"
}

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
  eval location=${3}
  eval population=${4}
  eval beta=${5}
  eval therapyId=${6}
  eval prmcSize=${7}
  eval ifRate=${8}
  eval startYear=${9}
  eval endYear=${10}
  eval replicates=${11}
  eval tag=${12}

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

  #ADMIN
  cp $HOME/Simulations/Scripts/${folder}/templates/sim_admin.asc $HOME/Simulations/Results/${tag}/config/sim_admin_${location}.asc
  echo "Copy $HOME/Simulations/Scripts/${folder}/templates/sim_admin.asc to $HOME/Simulations/Results/${tag}/config/sim_admin_${location}.asc"

  #IFR
  sed 's/#IFR#/'"${ifRate}"'/g' $HOME/Simulations/Scripts/${folder}/templates/sim_interrupted_feeding_rate.asc > $HOME/Simulations/Results/${tag}/config/sim_interrupted_feeding_rate_${location}_${ifRate}.asc
  echo "Edit & Copy IFR from $HOME/Simulations/Scripts/${folder}/templates/sim_interrupted_feeding_rate.asc to $HOME/Simulations/Results/${tag}/config/sim_interrupted_feeding_rate_${location}_${ifRate}.asc"

  #POP
  sed 's/#POPULATION#/'"${population}"'/g' $HOME/Simulations/Scripts/${folder}/templates/sim_pop.asc > $HOME/Simulations/Results/${tag}/config/sim_pop_${location}_${population}.asc
  echo "Edit & Copy POPULATION from $HOME/Simulations/Scripts/${folder}/templates/sim_pop.asc to $HOME/Simulations/Results/${tag}/config/sim_pop_${location}_${population}.asc"

  #BETA
  sed 's/#BETA#/'"${beta}"'/g' $HOME/Simulations/Scripts/${folder}/templates/sim_beta.asc > $HOME/Simulations/Results/${tag}/config/sim_beta_${location}_${beta}.asc
  echo "Edit & Copy BETA $HOME/Simulations/Scripts/${folder}/templates/sim_beta.asc to $HOME/Simulations/Results/${tag}/config/sim_beta_${location}_${beta}.asc"

  #TRAVEL
  cp $HOME/Simulations/Scripts/${folder}/templates/sim_travel.asc $HOME/Simulations/Results/${tag}/config/sim_travel_${location}.asc
  echo "Copy $HOME/Simulations/Scripts/${folder}/templates/sim_travel.asc to $HOME/Simulations/Results/${tag}/config/sim_travel_${location}.asc"

  #TM_O5
  cp $HOME/Simulations/Scripts/${folder}/templates/sim_treatment_o5.asc $HOME/Simulations/Results/${tag}/config/sim_treatment_o5_${location}.asc
  echo "Copy $HOME/Simulations/Scripts/${folder}/templates/sim_treatment_o5.asc to $HOME/Simulations/Results/${tag}/config/sim_treatment_o5_${location}.asc"

  #TM_U5
  cp $HOME/Simulations/Scripts/${folder}/templates/sim_treatment_u5.asc $HOME/Simulations/Results/${tag}/config/sim_treatment_u5_${location}.asc
  echo "Copy $HOME/Simulations/Scripts/${folder}/templates/sim_treatment_u5.asc to $HOME/Simulations/Results/${tag}/config/sim_treatment_u5_${location}.asc"

  for (( i=1; i<=$replicates; i++ ))
  do

    #
    #YML
    #

    cp  $HOME/Simulations/Scripts/${folder}/templates/sim_prmc.yml $HOME/Simulations/Results/${tag}/config/sim_prmc_${location}_${population}_${beta}_${therapyId}_${prmcSize}_${ifRate}_${tag}_${i}.yml
    echo "Copy $HOME/Simulations/Scripts/${folder}/templates/sim_prmc.yml to $HOME/Simulations/Results/${tag}/config/sim_prmc_${location}_${population}_${beta}_${therapyId}_${prmcSize}_${ifRate}_${tag}_${i}.yml"
    sleep 1

    sed -i 's/#USER#/'"${user}"'/g' $HOME/Simulations/Results/${tag}/config/sim_prmc_${location}_${population}_${beta}_${therapyId}_${prmcSize}_${ifRate}_${tag}_${i}.yml
    echo "Edit USER in $HOME/Simulations/Results/${tag}/config/sim_prmc_${location}_${population}_${beta}_${therapyId}_${prmcSize}_${ifRate}_${tag}_${i}.yml"
    sleep 1

    sed -i 's/#TAG#/'"${tag}"'/g' $HOME/Simulations/Results/${tag}/config/sim_prmc_${location}_${population}_${beta}_${therapyId}_${prmcSize}_${ifRate}_${tag}_${i}.yml
    echo "Edit TAG in $HOME/Simulations/Results/${tag}/config/sim_prmc_${location}_${population}_${beta}_${therapyId}_${prmcSize}_${ifRate}_${tag}_${i}.yml"
    sleep 1

    sed -i 's/#LOCATION#/'"${location}"'/g' $HOME/Simulations/Results/${tag}/config/sim_prmc_${location}_${population}_${beta}_${therapyId}_${prmcSize}_${ifRate}_${tag}_${i}.yml
    echo "Edit LOCATION in $HOME/Simulations/Results/${tag}/config/sim_prmc_${location}_${population}_${beta}_${therapyId}_${prmcSize}_${ifRate}_${tag}_${i}.yml"
    sleep 1

    sed -i 's/#POPULATION#/'"${population}"'/g' $HOME/Simulations/Results/${tag}/config/sim_prmc_${location}_${population}_${beta}_${therapyId}_${prmcSize}_${ifRate}_${tag}_${i}.yml
    echo "Edit POPULATION in $HOME/Simulations/Results/${tag}/config/sim_prmc_${location}_${population}_${beta}_${therapyId}_${prmcSize}_${ifRate}_${tag}_${i}.yml"
    sleep 1

    sed -i 's/#BETA#/'"${beta}"'/g' $HOME/Simulations/Results/${tag}/config/sim_prmc_${location}_${population}_${beta}_${therapyId}_${prmcSize}_${ifRate}_${tag}_${i}.yml
    echo "Edit BETA in $HOME/Simulations/Results/${tag}/config/sim_prmc_${location}_${population}_${beta}_${therapyId}_${prmcSize}_${ifRate}_${tag}_${i}.yml"
    sleep 1

    sed -i 's/#IFR#/'"${ifRate}"'/g' $HOME/Simulations/Results/${tag}/config/sim_prmc_${location}_${population}_${beta}_${therapyId}_${prmcSize}_${ifRate}_${tag}_${i}.yml
    echo "Edit IFR in $HOME/Simulations/Results/${tag}/config/sim_prmc_${location}_${population}_${beta}_${therapyId}_${prmcSize}_${ifRate}_${tag}_${i}.yml"
    sleep 1

    sed -i 's/#THERAPYID#/'"${therapyId}"'/g' $HOME/Simulations/Results/${tag}/config/sim_prmc_${location}_${population}_${beta}_${therapyId}_${prmcSize}_${ifRate}_${tag}_${i}.yml
    echo "Edit THERAPYID in $HOME/Simulations/Results/${tag}/config/sim_prmc_${location}_${population}_${beta}_${therapyId}_${prmcSize}_${ifRate}_${tag}_${i}.yml"
    sleep 1

    sed -i 's/#PRMCSIZE#/'"${prmcSize}"'/g' $HOME/Simulations/Results/${tag}/config/sim_prmc_${location}_${population}_${beta}_${therapyId}_${prmcSize}_${ifRate}_${tag}_${i}.yml
    echo "Edit PRMCSIZE in $HOME/Simulations/Results/${tag}/config/sim_prmc_${location}_${population}_${beta}_${therapyId}_${prmcSize}_${ifRate}_${tag}_${i}.yml"
    sleep 1

    sed -i 's/#STARTYEAR#/'"${startYear}"'/g' $HOME/Simulations/Results/${tag}/config/sim_prmc_${location}_${population}_${beta}_${therapyId}_${prmcSize}_${ifRate}_${tag}_${i}.yml
    echo "Edit STARTYEAR in $HOME/Simulations/Results/${tag}/config/sim_prmc_${location}_${population}_${beta}_${therapyId}_${prmcSize}_${ifRate}_${tag}_${i}.yml"
    sleep 1

    sed -i 's/#ENDYEAR#/'"${endYear}"'/g' $HOME/Simulations/Results/${tag}/config/sim_prmc_${location}_${population}_${beta}_${therapyId}_${prmcSize}_${ifRate}_${tag}_${i}.yml
    echo "Edit ENDYEAR in $HOME/Simulations/Results/${tag}/config/sim_prmc_${location}_${population}_${beta}_${therapyId}_${prmcSize}_${ifRate}_${tag}_${i}.yml"
    sleep 1

    #
    #PBS
    #

    cp $HOME/Simulations/Scripts/${folder}/templates/run_prmc.pbs $HOME/Simulations/Results/${tag}/log/run_prmc_${location}_${population}_${beta}_${therapyId}_${prmcSize}_${ifRate}_${tag}_${i}.pbs
    echo "Copy $HOME/Simulations/Scripts/${folder}/templates/run_prmc.pbs to $HOME/Simulations/Results/${tag}/log/run_prmc_${location}_${population}_${beta}_${therapyId}_${prmcSize}_${ifRate}_${tag}_${i}.pbs"
    dos2unix $HOME/Simulations/Results/${tag}/log/run_prmc_${location}_${population}_${beta}_${therapyId}_${prmcSize}_${ifRate}_${tag}_${i}.pbs
    sleep 1

    sed -i 's/#TAG#/'"${tag}"'/g' $HOME/Simulations/Results/${tag}/log/run_prmc_${location}_${population}_${beta}_${therapyId}_${prmcSize}_${ifRate}_${tag}_${i}.pbs
    echo "Edit TAG in $HOME/Simulations/Results/${tag}/log/run_prmc_${location}_${population}_${beta}_${therapyId}_${prmcSize}_${ifRate}_${tag}_${i}.pbs"
    sleep 1

  done

  cd $HOME/Simulations/Results/${tag}/log
  echo "cd $HOME/Simulations/Results/${tag}/log"

  for (( i=1; i<=$replicates; i++ ))
  do
    checkDelay ${user}
    qsub -F "${location} ${population} ${beta} ${therapyId} ${prmcSize} ${ifRate} ${tag} ${i}" run_prmc_${location}_${population}_${beta}_${therapyId}_${prmcSize}_${ifRate}_${tag}_${i}.pbs
    echo "qsub -F "${location} ${population} ${beta} ${therapyId} ${prmcSize} ${ifRate} ${tag} ${i}" run_prmc_${location}_${population}_${beta}_${therapyId}_${prmcSize}_${ifRate}_${tag}_${i}.pbs"
  done

  cd $HOME/Simulations/
  echo "Scheduled all simulations, back to $HOME/Simulations folder"
}