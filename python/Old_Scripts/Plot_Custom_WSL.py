# -*- coding: utf-8 -*-
"""
Created on Fri Jul 30 14:26:57 2021

@author: ktt5121
"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

#File vars
rep_year = "2021"
rep_month = "09"
rep_day = "02"
rep_hour = "13"
rep_date = rep_year + "_" + rep_month + "_" + rep_day + "_" + rep_hour 
rep_job = 0
rep_tags = [
            # "None",
            "SFT",
            # "5YearCycling",
            # "AdaptiveCycling",
            # "MFT"
            ]
rep_base_name = "Monthly_Data"
rep_ext = ".txt"
rep_prefix = "../output/"
rep_file = ""

#Data vars
rep_data_raw = 0
rep_data_observe = 0
rep_data_range = [2007,2038]
rep_total_location = 4
rep_locations = [
                  [0]
                ]
rep_headers = []
rep_headers_observe = []

#Plot
rep_location_colors = [ "cyan", "orange", "green", "purple", "yellow", "red" ]
                        
for tag in rep_tags:
    rep_file = rep_prefix + rep_date + "_" + rep_base_name + "_" + tag + "_" + str(rep_job) + rep_ext

rep_data_raw = pd.read_csv(rep_file)    
  
rep_data_observe = rep_data_raw[(rep_data_raw.Calendar >= rep_data_range[0]) & (rep_data_raw.Calendar <= rep_data_range[1])]
rep_headers = rep_data_raw.columns
   

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
"TreatmentCoverageLT5ByLocation",
"TreatmentCoverageMT5ByLocation",
"TodayRITFByLocation",
"TodayTFByLocation",
"TodayNumberOfTreatmentsByLocation",
"TodayNumberOfBitesByLocation",
"TodayImmuneByLocation",
"TodayImmuneLT5ByLocation",
"TodayImmuneMT5ByLocation",
"TodayParasitePopulationByLocation",
"TodayParasitePopulationLT5ByLocation",
"TodayParasitePopulationMT5ByLocation",
"ProbabilityToBeTreatedLT5ByLocation",
"ProbabilityToBeTreatedMT5ByLocation",
"EIRByLocation",
"EIRLog10ByLocation"
]

rep_x_observe = "Day"
# rep_x_observe = "Calendar"

rep_row_observe = 5;

fig, axes = plt.subplots(nrows=rep_row_observe, ncols=len(rep_tags),sharex="col", sharey=False, figsize = (200,80))
fig.subplots_adjust(top = 0.94, bottom = 0.06, right = 0.95, left = 0.05, hspace=0.35, wspace = 0.2)

x_tick_observe = range(rep_data_range[0],rep_data_range[1],1)

#Ploting
for col,tag_index in zip(range(len(rep_tags)),range(len(rep_tags))):
    for row in range(0,rep_row_observe):
        index = (row)*(len(rep_tags))+(tag_index) + 1
        plt.subplot(rep_row_observe,len(rep_tags),index)
        if row == 0:                  
            for location_index in rep_locations[tag_index]:
                g = sns.lineplot(data = rep_data_observe, 
                                    x = rep_x_observe,
                                    y = rep_data_observe["BloodSlidePrevalenceByLocation"+str(location_index)],
                                    ci=None)
                g.set(xlabel=None)
                g.set(ylabel=None)
            plt.title(rep_tags[tag_index])
            plt.ylabel("Prevalence")
        if row == 1:                 
            for location_index in rep_locations[tag_index]:                
                g = sns.lineplot(data = rep_data_observe, 
                                    x = rep_x_observe,
                                    y = rep_data_observe["ProbabilityToBeTreatedLT5ByLocation"+str(location_index)],
                                    ci=None)
                g.set(xlabel=None)
                g.set(ylabel=None)
                # plt.yticks(np.arange (0, 1, 0.25))
            # plt.xticks(x_tick_observe)
            plt.ylabel("TC LT5")
        if row == 2:                 
            for location_index in rep_locations[tag_index]:                
                g = sns.lineplot(data = rep_data_observe, 
                                    x = rep_x_observe,
                                    y = rep_data_observe["MonthlyNumberOfTreatmentByLocation"+str(location_index)],
                                    ci=None)
                g.set(xlabel=None)
                g.set(ylabel=None)
                # plt.yticks(np.arange (0, 1, 0.25))
            # plt.xticks(x_tick_observe)
            plt.ylabel("Treatment")
        if row == 3:                 
            for location_index in rep_locations[tag_index]:                
                g = sns.lineplot(data = rep_data_observe, 
                                    x = rep_x_observe,
                                    y = rep_data_observe["CurrentForceOfInfectionByLocation"+str(location_index)+"ParasiteType""128.64"],
                                    ci=None)
                g.set(xlabel=None)
                g.set(ylabel=None)
                # plt.yticks(np.arange (0, 1, 0.25))
            # plt.xticks(x_tick_observe)
            plt.ylabel("FOI - 128.64")
        if row == 4:                 
            for location_index in rep_locations[tag_index]:                
                g = sns.lineplot(data = rep_data_observe, 
                                    x = rep_x_observe,
                                    y = rep_data_observe["CurrentForceOfInfectionByLocation"+str(location_index)+"ParasiteType""128.72"],
                                    ci=None)
                # g.set(xlabel=None)
                # g.set(ylabel=None)
                g.set(xlabel=None)
                g.set(ylabel=None)
            # plt.yticks(range(0,20,0.1))
            # plt.xticks(x_tick_observe)
            plt.ylabel("FOI - 128.72")
                
fig.legend(loc='lower center', labels=[str(i+1) for i in rep_locations[0]], ncol = len(rep_locations[0]))
plt.show()