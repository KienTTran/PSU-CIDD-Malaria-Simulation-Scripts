#!/bin/bash

function check_delay {
  eval user='ktt5121'
  while [ `qstat -u $user | grep $user | wc -l` -gt $LIMIT ]; do
    sleep 10s
  done
}

function runReplicatesMutationOff() {

  sed 's/#POPULATION#/'"$1"'/g' templates/bfa_pop_4.asc > ../bfa_pop_4_$1.asc
    echo "Copy templates/bfa_pop_4.asc to ../bfa_pop_4_$1.asc"

  for (( i=1; i<=$2; i++ ))
  do
#    sed 's/#POPULATION#/'"$1"'/g' templates/Demo_None_Mutation_Off.yml > ../Demo_None_Mutation_Off_$1_$3_$i.yml
#    echo "Copy .templates/Demo_None_Mutation_Off.yml to ../Demo_None_Mutation_Off_$1_$3_$i.yml"
#    sleep 1
#    sed 's/#POPULATION#/'"$1"'/g' templates/Run_None_Mutation_Off.pbs > Run_None_Mutation_Off_$1_$3_$i.pbs
#    echo "Copy templates/Run_None_Mutation_Off.pbs to ../Run_None_Mutation_Off_$1_$3_$i.pbs"
#    sleep 1
    
    sed 's/#POPULATION#/'"$1"'/g' templates/Demo_SFT_Mutation_Off.yml > ../Demo_SFT_Mutation_Off_$1_$3_$i.yml
    echo "Copy templates/Demo_SFT_Mutation_Off.yml to ../Demo_SFT_Mutation_Off_$1_$3_$i.yml"
    sleep 1
    sed 's/#POPULATION#/'"$1"'/g' templates/Run_SFT_Mutation_Off.pbs > Run_SFT_Mutation_Off_$1_$3_$i.pbs
    echo "Copy templates/Run_SFT_Mutation_Off.pbs to ../Run_SFT_Mutation_Off_$1_$3_$i.pbs"
    sleep 1
    
    sed 's/#POPULATION#/'"$1"'/g' templates/Demo_5YearCycling_Mutation_Off.yml > ../Demo_5YearCycling_Mutation_Off_$1_$3_$i.yml
    echo "Copy templates/Demo_5YearCycling_Mutation_Off.yml to ../Demo_5YearCycling_Mutation_Off_$1_$3_$i.yml"
    sleep 1
    sed 's/#POPULATION#/'"$1"'/g' templates/Run_5YearCycling_Mutation_Off.pbs > Run_5YearCycling_Mutation_Off_$1_$3_$i.pbs
    echo "Copy templates/Run_5YearCycling_Mutation_Off.pbs to ../Run_5YearCycling_Mutation_Off_$1_$3_$i.pbs"
    sleep 1
    
    sed 's/#POPULATION#/'"$1"'/g' templates/Demo_AdaptiveCycling_Mutation_Off.yml > ../Demo_AdaptiveCycling_Mutation_Off_$1_$3_$i.yml
    echo "Copy templates/Demo_AdaptiveCycling_Mutation_Off.yml to ../Demo_AdaptiveCycling_Mutation_Off_$1_$3_$i.yml"
    sleep 1
    sed 's/#POPULATION#/'"$1"'/g' templates/Run_AdaptiveCycling_Mutation_Off.pbs > Run_AdaptiveCycling_Mutation_Off_$1_$3_$i.pbs
    echo "Copy templates/Run_AdaptiveCycling_Mutation_Off.pbs to ../Run_AdaptiveCycling_Mutation_Off_$1_$3_$i.pbs"
    sleep 1
    
    sed 's/#POPULATION#/'"$1"'/g' templates/Demo_MFT_Mutation_Off.yml > ../Demo_MFT_Mutation_Off_$1_$3_$i.yml
    echo "Copy templates/Demo_MFT_Mutation_Off.yml to ../Demo_MFT_Mutation_Off_$1_$3_$i.yml"
    sleep 1
    sed 's/#POPULATION#/'"$1"'/g' templates/Run_MFT_Mutation_Off.pbs > Run_MFT_Mutation_Off_$1_$3_$i.pbs
    echo "Copy templates/Run_MFT_Mutation_Off.pbs to ../Run_MFT_Mutation_Off_$1_$3_$i.pbs"
    sleep 1
    
  done

  for (( i=1; i<=$2; i++ ))
  do
    check_delay
#    qsub -F "$1 $i $3" Run_None_Mutation_Off_$1_$3_$i.pbs
#    echo "qsub -F $1 $i $3 Run_None_Mutation_Off_$1_$3_$i.pbs"
    qsub -F "$1 $i $3" Run_SFT_Mutation_Off_$1_$3_$i.pbs
    echo "qsub -F $1 $i $3 Run_SFT_Mutation_Off_$1_$3_$i.pbs"
    qsub -F "$1 $i $3" Run_5YearCycling_Mutation_Off_$1_$3_$i.pbs
    echo "qsub -F $1 $i $3 Run_5YearCycling_Mutation_Off_$1_$3_$i.pbs"
    qsub -F "$1 $i $3" Run_AdaptiveCycling_Mutation_Off_$1_$3_$i.pbs
    echo "qsub -F $1 $i $3 Run_AdaptiveCycling_Mutation_Off_$1_$3_$i.pbs"
    qsub -F "$1 $i $3" Run_MFT_Mutation_Off_$1_$3_$i.pbs
    echo "qsub -F $1 $i $3 Run_MFT_Mutation_Off_$1_$3_$i.pbs"
  done
}
