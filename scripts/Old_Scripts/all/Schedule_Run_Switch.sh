#!/bin/bash

function check_delay {
  eval user='ktt5121'
  while [ `qstat -u $user | grep $user | wc -l` -gt $LIMIT ]; do
    sleep 10s
  done
}

function runReplicatesSwitch() {

  eval population=$1
  eval switchyear=$2
  eval switchid=$3
  eval replicates=$4
  eval tag=$5

  sed 's/#POPULATION#/'"$population"'/g' templates/bfa_pop_4.asc > ../bfa_pop_4_$population.asc
    echo "Copy templates/bfa_pop_4.asc to ../bfa_pop_4_$population.asc"

  mkdir "../analysis/$tag"
  echo "Created folder $tag in ../analysis"
  sleep 1

  mkdir "../analysis/$tag/$population"
  echo "Created folder $population in ../analysis/$tag/"
  sleep 1

  mkdir "../analysis/$tag/$population/config"
  echo "Created folder config in ../analysis/$tag/$population"
  sleep 1

  mkdir "../analysis/$tag/$population/log"
  echo "Created folder log in ../analysis/$tag/$population"
  sleep 1

  mkdir "../analysis/$tag/$population/output"
  echo "Created folder output in ../analysis/$tag/$population"
  sleep 1

  for (( i=1; i<=$replicates; i++ ))
  do

    sed 's/#POPULATION#/'"$population"'/g' templates/Demo_Switch.yml > ../analysis/$tag/$population/config/Demo_Switch_$population_$switchyear_$switchid_$tag_$i.yml
    echo "Edit POPULATION & copy templates/Demo_Switch.yml to ../analysis/$tag/$population/config/Demo_Switch_$population_$switchyear_$switchid_$tag_$i.yml"
    sleep 1

    sed -i 's/#SWITCH_YEAR#/'"$switchyear"'/g' ../analysis/$tag/$population/config/Demo_Switch_$population_$switchyear_$switchid_$tag_$i.yml
    echo "Edit SWITCH_YEAR ../analysis/$tag/$population/config/Demo_Switch_$population_$switchyear_$switchid_$tag_$i.yml"
    sleep 1

    sed -i 's/#SWITCH_ID#/'"$switchid"'/g' ../analysis/$tag/$population/config/Demo_Switch_$population_$switchyear_$switchid_$tag_$i.yml
    echo "Edit SWITCH_ID ../analysis/$tag/$population/config/Demo_Switch_$population_$switchyear_$switchid_$tag_$i.yml"
    sleep 1
    
    sed 's/#POPULATION#/'"$population"'/g' templates/Run_Switch.pbs > ../analysis/$tag/$population/log/Run_Switch_$population_$switchyear_$switchid_$tag_$i.pbs
    echo "Edit POPULATION & copy templates/Run_Switch.pbs to ../analysis/$tag/$population/log/Run_Switch_$population_$switchyear_$switchid_$tag_$i.pbs"
    sleep 1

    sed -i 's/#SWITCH_YEAR#/'"$switchyear"'/g' ../analysis/$tag/$population/log/Run_Switch_$population_$switchyear_$switchid_$tag_$i.pbs
    echo "Edit SWITCH_YEAR ../analysis/$tag/$population/log/Run_Switch_$population_$switchyear_$switchid_$tag_$i.pbs"
    sleep 1

    sed -i 's/#SWITCH_ID#/'"$switchid"'/g' ../analysis/$tag/$population/log/Run_Switch_$population_$switchyear_$switchid_$tag_$i.pbs
    echo "Edit SWITCH_ID ../analysis/$tag/$population/log/Run_Switch_$population_$switchyear_$switchid_$tag_$i.pbs"
    sleep 1
    
  done

  cd ../analysis/$tag/$population/log
  echo "cd ../analysis/$tag/$population/log"

  for (( i=1; i<=$replicates; i++ ))
  do
    check_delay
    qsub -F "$population $switchyear $switchid $tag $i" Run_Switch_$population_$switchyear_$switchid_$tag_$i.pbs
    echo "qsub -F $population $switchyear $switchid $tag $i Run_Switch_$population_$switchyear_$switchid_$tag_$i.pbs"
  done
}
