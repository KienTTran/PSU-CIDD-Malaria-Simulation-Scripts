#!/bin/bash
source Scripts/PRMC_4_Genotypes_Exp_1/Schedule_Run_PRMC.sh &&
runReplicates ktt5121 PRMC_4_Genotypes_Exp_1 #binary# #location# #population# #beta# #therapy_id# #prmc_size# #ifr# #start_year# #end_year# #replicates# PRMC_4_Genotypes_Exp_1_#beta#_#ifr# &&
