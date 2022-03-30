# -*- coding: utf-8 -*-
"""
Created on Fri Jul 30 14:26:57 2021

@author: ktt5121
"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from functools import reduce

#File vars
rep_year = "2021"
rep_month = "10"
rep_day = "04"
rep_hour = "12"
rep_pop = 50000
rep_mutation = "Mutation_On"
rep_date = rep_year + "_" + rep_month + "_" + rep_day + "_" + rep_hour 
rep_strategies = [
            # str(rep_pop) + "_None",
            # str(rep_pop) +"_SFT",
            # str(rep_pop) + "5YearCycling",
            # str(rep_pop) +"_AdaptiveCycling",
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
# rep_data_quantile_observe = pd.concat(rep_data_concat).quantile(axis=0)
    
# Overide headers
rep_headers_observe = [
# "ArtResistanceFrequencyAt15",
"CurrentNumberOfMutationEvents",
# "CurrentUTlDuration",
# "DiscountedAFU",
# "DiscountedAMUForClinicalCausedParasite",
# "DiscountedAMUPerParasitePopulation",
# "DiscountedAMUPerPerson",
"DoubleResistanceFrequencyAt15",
# "MeanMOI",
# "QuadrupleResistanceFrequencyAt15",
# "QuintupleResistanceFrequencyAt15",
# "SingleResistanceFrequencyAt15",
# "TFAt15",
# "TotalResistanceFrequencyAt15",
"BloodSlidePrevalenceByLocation",
# "BirthsByLocation",
# "BloodSlideNumberLT5ByLocation",
# "BloodSlideNumberMT5ByLocation",
"CurrentEIRByLocation",
# "CurrentTFByLocation",
# "CurrentRITFByLocation",
# "CumulativeNTFByLocation",
# "CumulativeClinicalEpisodesByLocation",
# "CumulativeDiscountedNTFByLocation",
# "CumulativeMutantsByLocation",
# "DeathsByLocation",
# "FractionOfPositiveThatAreClinicalByLocation",
# "MalariaDeathsByLocation",
# "MalariaDeathsLT5ByLocation",
# "MalariaDeathsMT5ByLocation",
# "MonthlyNumberOfClinicalEpisodeByLocation",
"MonthlyNumberOfNewInfectionsByLocation",
# "MonthlyNumberOfTreatmentByLocation",
# "MonthlyNumberOfTreatmentFailureByLocation",
# "MonthlyNumberOfNonTreatmentByLocation",
# "NumberOfClinicalLT5ByLocation",
# "NumberOfClinicalMT5ByLocation",
# "NumberOfDeathLT5ByLocation",
"NumberOFDeathMT5ByLocation",
"NumberOfPositiveByLocation",
# "PercentageBitesOnTop20ByLocation",
"PopulationSizeByLocation",
# "PopulationSizeResidenceByLocation",
# "TodayRITFByLocation",
# "TodayTFByLocation",
# "TodayNumberOfTreatmentsByLocation",
# "TotalNumberOfBitesByLocation",
# "TotalImmuneByLocation",
# "TotalImmuneLT5ByLocation",
# "TotalImmuneMT5ByLocation",
"TotalParasitePopulationByLocation",
"TotalParasitePopulationLT5ByLocation",
"TotalParasitePopulationMT5ByLocation",
# "ProbabilityToBeTreatedLT5ByLocation",
# "ProbabilityToBeTreatedMT5ByLocation",
# "EIRByLocation",
# "EIRLog10ByLocation"
]
# rep_headers_observe = [
# "ArtResistanceFrequencyAt15",
# "CurrentNumberOfMutationEvents",
# "CurrentEIRByLocation",
# "CumulativeMutantsByLocation",
# "DeathsByLocation",
# "FractionOfPositiveThatAreClinicalByLocation",
# "MalariaDeathsByLocation",
# "MonthlyNumberOfClinicalEpisodeByLocation",
# ]
# rep_x_observe = "Day"
rep_x_observe = "Calendar"

# Rows = Tot // Cols 
# Rows += Tot % Cols
rep_cols_observe = 2;
# rep_rows_observe = 6;
rep_rows_observe = int(len(rep_headers_observe) / rep_cols_observe);

fig, axes = plt.subplots(nrows=rep_rows_observe, ncols=rep_cols_observe,sharex=True, sharey=True, figsize = (250,100))
fig.subplots_adjust(top = 0.94, bottom = 0.06, right = 0.95, left = 0.05, hspace=0.35, wspace = 0.15)

x_tick_observe = range(rep_data_range[0],rep_data_range[1],5)

def truncate_header(header):
    header_new = header
    if "ByLocation" in header:
        header_new = header_new.replace("ByLocation","")
    if "Monthly" in header:
        header_new = header_new.replace("Monthly","M")
    if "Current" in header:
        header_new = header_new.replace("Current","C")
    if "Probability" in header:
        header_new = header_new.replace("Probability","P")
    if "Cumulative" in header:
        header_new = header_new.replace("Cumulative","CC")
    if "Population" in header:
        header_new = header_new.replace("Population","Pop")
        
    return header_new
    
#Ploting
for col_index in range(0,rep_cols_observe):
    for row_index in range(0,rep_rows_observe):
        index = (row_index)*(rep_cols_observe)+(col_index)
        plt.subplot(rep_rows_observe,rep_cols_observe,index+1) 
        if "ByLocation" in rep_headers_observe[index]:
            print("Location: " + str(index) + "/" + str(len(rep_headers_observe)) + ": " + rep_headers_observe[index])
            for location_index in rep_locations[0]:
                g = sns.lineplot(data = rep_data_mean_observe, 
                                  x = rep_x_observe,
                                  y = rep_headers_observe[index]+str(location_index),
                                  ci = None)
                g = sns.lineplot(data = rep_data_max_observe, 
                                  x = rep_x_observe,
                                  y = rep_headers_observe[index]+str(location_index),
                                  ci = None)
                g = sns.lineplot(data = rep_data_min_observe, 
                                  x = rep_x_observe,
                                  y = rep_headers_observe[index]+str(location_index),
                                  ci = None)
                # plt.fill_between(rep_data_mean_observe[rep_x_observe],
                #              # rep_data_mean_observe[rep_headers_observe[index]+str(location_index)] - 0.5,
                #              rep_data_mean_observe[rep_headers_observe[index]+str(location_index)],
                #              interpolate=True,
                #              color="blue",
                #              alpha=0.5)
                g.set(xlabel=None)
                g.set(ylabel=None)
        else:
            print(str(index) + "/" + str(len(rep_headers_observe)) + ": " + rep_headers_observe[index])
            g = sns.lineplot(data = rep_data_mean_observe, 
                              x = rep_x_observe,
                              y = rep_headers_observe[index],
                              ci = "sd")   
            g.set(xlabel=None)
            g.set(ylabel=None)
        plt.xticks(x_tick_observe,fontsize=8)
        plt.yticks(fontsize=8)
        plt.title(rep_headers_observe[index],fontsize=10,pad=0.1)    
        # if row_index == rep_rows_observe - 1:
            # plt.xlabel(rep_x_observe,fontsize=8)
        
fig.legend(labels=[str(i) for i in rep_locations[0]], loc='lower center', ncol=rep_cols_observe)
fig.suptitle(rep_strategies[0]+"_"+rep_tag)
plt.show()