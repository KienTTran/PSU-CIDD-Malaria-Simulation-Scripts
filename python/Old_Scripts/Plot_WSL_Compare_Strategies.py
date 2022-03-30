# -*- coding: utf-8 -*-
"""
Created on Fri Jul 30 14:26:57 2021

@author: ktt5121
"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

#File vars
rep_year = "2021"
rep_month = "08"
rep_day = "29"
rep_hour = "02"
rep_pop = 50000
rep_mutation = "Mutation_On"
rep_date = rep_year + "_" + rep_month + "_" + rep_day + "_" + rep_hour 
rep_strategies = [
            # str(rep_pop) + "_None",
            str(rep_pop) +"_SFT",
            str(rep_pop) + "_5YearCycling",
            str(rep_pop) +"_AdaptiveCycling",
            str(rep_pop) + "_MFT"
            ]
rep_tag = rep_mutation + "_Test_TC"
rep_base_name = "Monthly_Data"
rep_ext = ".txt"
rep_prefix = "../analysis/" + str(rep_pop) + "/"
rep_files = []

#Data vars
rep_data_raw = []
rep_data_observe = []
rep_data__mean_observe = []
rep_data_range = [2007,2037]
rep_total_location = 4
rep_jobs = 5
rep_locations = [
                  [0],
                  [0],
                  [0],
                  [0],
                  [0]
                ]
rep_headers = []
rep_headers_observe = []

#Plot
rep_location_colors = [ "cyan", "orange", "green", "purple", "yellow", "red" ]
                        
for strategy in rep_strategies:
    for job in range(1,rep_jobs+1):
        rep_files.append(rep_prefix + rep_date + "_" + rep_base_name + "_" + strategy + "_" + rep_tag + "_" + str(job) + rep_ext)

for file in rep_files:
    rep_data_raw.append(pd.read_csv(file))
    
for data in rep_data_raw:    
    rep_data_observe.append(data[(data.Calendar > rep_data_range[0]) & (data.Calendar < rep_data_range[1])])
    rep_headers = data.columns
   
rep_data_concat = [rep_data for rep_data in rep_data_observe]             
rep_data_mean_observe = pd.concat(rep_data_concat).mean(level=0)            
rep_data_min_observe = pd.concat(rep_data_concat).min(level=0)          
rep_data_max_observe = pd.concat(rep_data_concat).max(level=0)

#Overide headers
rep_headers_observe = [
"ArtResistanceFrequencyAt15",
"CurrentNumberOfMutationEvents",
"CurrentUTlDuration",
"DiscountedAFU",
"DiscountedAMUForClinicalCausedParasite",
"DiscountedAMUPerParasitePopulation",
"DiscountedAMUPerPerson",
"DoubleResistanceFrequencyAt15",
"MeanMOI",
"QuadrupleResistanceFrequencyAt15",
"QuintupleResistanceFrequencyAt15",
"SingleResistanceFrequencyAt15",
"TFAt15",
"TotalResistanceFrequencyAt15",
"BloodSlidePrevalenceByLocation",
"BirthsByLocation",
"BloodSlideNumberLT5ByLocation",
"BloodSlideNumberMT5ByLocation",
"CurrentEIRByLocation",
"CurrentTFByLocation",
"CurrentRITFByLocation",
"CumulativeNTFByLocation",
"CumulativeClinicalEpisodesByLocation",
"CumulativeDiscountedNTFByLocation",
"CumulativeMutantsByLocation",
"DeathsByLocation",
"FractionOfPositiveThatAreClinicalByLocation",
"MalariaDeathsByLocation",
"MalariaDeathsLT5ByLocation",
"MalariaDeathsMT5ByLocation",
"MonthlyNumberOfClinicalEpisodeByLocation",
"MonthlyNumberOfNewInfectionsByLocation",
"MonthlyNumberOfTreatmentByLocation",
"MonthlyNumberOfTreatmentFailureByLocation",
"MonthlyNumberOfNonTreatmentByLocation",
"NumberOfClinicalLT5ByLocation",
"NumberOfClinicalMT5ByLocation",
"NumberOfDeathLT5ByLocation",
"NumberOFDeathMT5ByLocation",
"NumberOfPositiveByLocation",
"PercentageBitesOnTop20ByLocation",
"PopulationSizeByLocation",
"PopulationSizeResidenceByLocation",
"TodayRITFByLocation",
"TodayTFByLocation",
"TodayNumberOfTreatmentsByLocation",
"TotalNumberOfBitesByLocation",
"TotalImmuneByLocation",
"TotalImmuneLT5ByLocation",
"TotalImmuneMT5ByLocation",
"TotalParasitePopulationByLocation",
"TotalParasitePopulationLT5ByLocation",
"TotalParasitePopulationMT5ByLocation",
"ProbabilityToBeTreatedLT5ByLocation",
"ProbabilityToBeTreatedMT5ByLocation"
"EIRByLocation",
"EIRLog10ByLocation"
]
rep_x_observe = "Calendar"

rep_row_observe = 4;

fig, axes = plt.subplots(nrows=rep_row_observe, ncols=len(rep_strategies),sharex=True, sharey=True, figsize = (200,80))
fig.subplots_adjust(top = 0.94, bottom = 0.06, right = 0.95, left = 0.05, hspace=0.35, wspace = 0.2)

x_tick_observe = range(rep_data_range[0],rep_data_range[1],5)

#Ploting
for col,tag_index in zip(range(len(rep_strategies)),range(len(rep_strategies))):
    for row in range(0,rep_row_observe):
        index = (row)*(len(rep_strategies))+(tag_index) + 1
        plt.subplot(rep_row_observe,len(rep_strategies),index)
        if row == 0:                     
            for location_index in rep_locations[tag_index]:
                g = sns.lineplot(data = rep_data_observe[tag_index], 
                                    x = rep_x_observe,
                                    y = rep_data_observe[tag_index]["PopulationSizeByLocation"+str(location_index)] \
                                        * rep_data_observe[tag_index]["BloodSlidePrevalenceByLocation"+str(location_index)],
                                    ci=None)
                g.set(xlabel=None)
                g.set(ylabel=None)
                # plt.yticks(np.arange (300, 800, 100))
            plt.xticks(x_tick_observe)
            plt.title(rep_strategies[tag_index])
            if col == 0:
                plt.ylabel("Prevalence Population")
        if row == 1:                 
            for location_index in rep_locations[tag_index]:
                
                g = sns.lineplot(data = rep_data_observe[tag_index], 
                                    x = rep_x_observe,
                                    y = rep_data_observe[tag_index]["TotalParasitePopulationByLocation"+str(location_index)],
                                    ci=None)
                g.set(xlabel=None)
                g.set(ylabel=None)
                # plt.yticks(np.arange (0, 1, 0.25))
            plt.xticks(x_tick_observe)
            if col == 0:
                plt.ylabel("MTreatment")
        if row == 2:              
            for location_index in rep_locations[tag_index]:
                g = sns.lineplot(data = rep_data_observe[tag_index], 
                                    x = rep_x_observe,
                                    y = rep_data_observe[tag_index]["TotalResistanceFrequencyAt15"],
                                    ci=None)
                g.set(xlabel=None)
                g.set(ylabel=None)
            plt.xticks(x_tick_observe)
                # plt.yticks(np.arange (25, 100, 25))
            if col == 0:
                plt.ylabel("TotalResistanceFrequencyAt15")
        if row == 3:                 
            for location_index in rep_locations[tag_index]:
                g = sns.lineplot(data = rep_data_observe[tag_index], 
                                    x = rep_x_observe,
                                    y = rep_data_observe[tag_index]["MalariaDeathsByLocation"+str(location_index)],
                                    ci=None)
                g.set(xlabel=None)
                g.set(ylabel=None)
                # plt.yticks(np.arange (0, 100, 25))
            plt.xlabel(rep_x_observe)
            plt.xticks(x_tick_observe)
            if col == 0:
                plt.ylabel("MalariaDeaths")
        if row == 4:                 
            for location_index in rep_locations[tag_index]:
                g = sns.lineplot(data = rep_data_observe[tag_index], 
                                    x = rep_x_observe,
                                    y = rep_data_observe[tag_index]["TotalParasitePopulationLT5ByLocation"+str(location_index)],
                                    ci=None)
                g.set(xlabel=None)
                g.set(ylabel=None)
                # plt.yticks(np.arange (0, 100, 25))
            plt.xlabel(rep_x_observe)
            plt.xticks(x_tick_observe)
            if col == 0:
                plt.ylabel("TotalParasitePopLT5")

plt.show()