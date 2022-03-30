# -*- coding: utf-8 -*-
"""
Created on Fri Jul 30 14:26:57 2021

@author: ktt5121
"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import operator
import math

#File vars
rep_year = "2021"
rep_month = "08"
rep_day = "30"
rep_hour = "00"
rep_pop = 50000
rep_data_range = [2007,2037]
rep_total_location = 4
rep_jobs = 1
rep_mutation = "Mutation_On"
rep_name = "Test_Baseline"
rep_date = rep_year + "_" + rep_month + "_" + rep_day + "_" + rep_hour 
rep_strategies = [
            # str(rep_pop) + "_None",
            # str(rep_pop) +"_SFT",
            # str(rep_pop) + "5YearCycling",
            # str(rep_pop) +"_AdaptiveCycling",
            str(rep_pop) + "_MFT"
            ]
rep_tag = rep_mutation + "_" + rep_name
rep_base_name = "Monthly_Data"
rep_ext = ".txt"
rep_prefix = "../analysis/" + rep_name + "/" + str(rep_pop) + "/"
rep_files = []

#Data vars
rep_data_raw = []
rep_data_observe = []
rep_data__mean_observe = []
rep_locations = [
                  [0,3]
                ]
rep_headers = []

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
    
rep_data_mean_observe["Year"] = rep_data_mean_observe.Calendar - rep_data_range[0]
        
#Plot vars
plot_lines = []
plot_labels = []
ops = { 
       "+": operator.add, 
       "-": operator.sub,
       "x": operator.mul,
       "/": operator.truediv
       }
        
def plot_one_header_CI(header, data, col_index, row_index, confident_interval):
    # print("row_index: " + str(row_index))
    # print("col_index: " + str(col_index))
    if "ByLocation" in header:
        for location_index in rep_locations[0]: 
            sns.lineplot(data = data, 
                        x = rep_x_observe,
                        y = header+str(location_index),
                        ax = axes[row_index,col_index],
                        ci = confident_interval) 
    else:
        sns.lineplot(data = data, 
                    x = rep_x_observe,
                    y = header,
                    ax = axes[row_index,col_index],
                    ci = confident_interval)
    
def plot_two_headers_ops(header1, header2, data, col_index, row_index, op, confident_interval):
    if "ByLocation" in header1:
        for location_index in rep_locations[0]:                    
              sns.lineplot(data = data, 
                        x = rep_x_observe,
                        y = ops[op](data[header1+str(location_index)],
                                    data[header2+str(location_index)]),
                        ax = axes[row_index,col_index],
                        ci = confident_interval)
    else:
        sns.lineplot(data = data, 
                    x = rep_x_observe,
                    y = ops[op](data[header1],
                                data[header2]),
                    ax = axes[row_index,col_index],
                    ci = confident_interval)
    axes[row_index,col_index].set_title(short_header(header1)+ op +short_header(header2),fontsize=8)
    axes[row_index,col_index].title.set_position([.5, 1.1])
        
def plot_one_header(header, data, col_index, row_index, confident_interval):
    plot_one_header_CI(header, data, col_index, row_index, confident_interval)
    # plot_one_header_2M(header, tag_index, header_index,confident_interval)
    axes[row_index,col_index].set_title(short_header(header),fontsize=8)
    axes[row_index,col_index].set_ylabel(None)
    
def plot_headers(header, data, col_index, row_index, confident_interval):
    if type(header) is list:
        plot_two_headers_ops(header[0], header[1], data, col_index, row_index, header[2], confident_interval)
    else:
        plot_one_header(header, data, col_index, row_index, confident_interval)
            
        
def short_header(header):
    new_header = header
    words = {
                "ByLocation":"",
                "Current":"Cr.",  
                "Probability":"P.",  
                "Total":"T.",  
                "Monthly":"M.", 
                "Malaria":"Ma.",  
                "Parasite":"Par.",    
                "BloodSlidePrevalence":"Pre.",  
                "Prevalence":"Pre.", 
                "Treatment":"Treat.",
                "Population":"Pop.",  
                "Cumulative":"Cu.",  
                "Resistance":"Res.",  
                "Mutation":"Mut.", 
                "NumberOf":"No.",  
                "Frequency":"Freq.",  
                "Clinical":"Cli.", 
                "Positive":"Pos.",
            }    
    for key in words:
        if key in header:
            new_header = new_header.replace(key,words[key])
    return new_header
    
#Overide headers
rep_headers_output = [
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

# rep_x_observe = "Calendar"
rep_x_observe = "Year"
# rep_x_observe = "Day"

# x_tick_observe = range(rep_data_range[0],rep_data_range[1],5)
x_tick_observe = []

if rep_x_observe == "Year":
    x_tick_observe = range(0,rep_data_range[1]-rep_data_range[0],5)   
    # for year in rep_data_mean_observe[0][0].Calendar:
    #     x_tick_observe.append(year - rep_data_range[0])
else:
    x_tick_observe = range(rep_data_range[0],rep_data_range[1],5)   

confident_interval = None

rep_header_observe = [
                        ["BloodSlidePrevalenceByLocation","PopulationSizeByLocation","x"],
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
                        "ProbabilityToBeTreatedMT5ByLocation",
                        "EIRByLocation",
                        "EIRLog10ByLocation"
                        ]

rep_rows_observe = 12
rep_cols_observe = math.ceil(len(rep_header_observe) / rep_rows_observe)

fig, axes = plt.subplots(nrows=rep_rows_observe, 
                         ncols=rep_cols_observe,
                         sharex="col", sharey=False, 
                         figsize = (300,100))
fig.subplots_adjust(top = 0.94, bottom = 0.06, right = 0.95, left = 0.05, hspace=0.2, wspace = 0.2)
sns.set_style("darkgrid")
   
#Ploting
header_index = 0
for col_index in range(0,rep_cols_observe):
    for row_index in range(0,rep_rows_observe):
        if header_index < len(rep_header_observe):
            plot_headers(rep_header_observe[header_index], rep_data_mean_observe, col_index, row_index, confident_interval)
            header_index += 1
        
plt.xticks(x_tick_observe)
fig.legend(loc='lower center', labels=[str(i) for i in rep_locations[0]], ncol = len(rep_strategies))