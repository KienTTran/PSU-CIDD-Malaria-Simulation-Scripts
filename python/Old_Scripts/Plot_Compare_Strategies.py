# -*- coding: utf-8 -*-
"""
Created on Fri Jul 30 14:26:57 2021

@author: ktt5121
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import operator

sns.reset_orig()

#File vars
rep_year = "2021"
rep_month = "08"
rep_day = "29"
rep_hour = "02"
rep_pop = 50000
rep_data_range = [2007,2038]
rep_total_location = 4
rep_jobs = 5
rep_mutation = "Mutation_Off"
rep_name = "Test_TC"
rep_date = rep_year + "_" + rep_month + "_" + rep_day + "_" + rep_hour 
rep_strategies = [
            # str(rep_pop) + "_None",
            str(rep_pop) +"_SFT",
            str(rep_pop) + "_5YearCycling",
            str(rep_pop) +"_AdaptiveCycling",
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
rep_data_mean_observe = []
rep_data_max_observe = []
rep_data_min_observe = []
rep_data_concat = []
rep_locations = [
                  [0,1,2,3],
                  [0,1,2,3],
                  [0,1,2,3],
                  [0,1,2,3],
                  [0,1,2,3]
                ]
rep_headers = []
rep_headers_observe = []

#Plot
rep_location_colors = [ "cyan", "orange", "green", "purple", "yellow", "red" ]
                        
for index,strategy in enumerate(rep_strategies):
    rep_data_raw.append([])
    rep_data_observe.append([])
    rep_data_mean_observe.append([])
    rep_data_max_observe.append([])
    rep_data_min_observe.append([])
    rep_data_concat.append([])
    rep_files.append([])
    for job in range(1,rep_jobs+1):
        rep_files[index].append(rep_prefix + rep_date + "_" + rep_base_name + "_" + strategy + "_" + rep_tag + "_" + str(job) + rep_ext)

for i,rep_strategy in enumerate(rep_files):
    for j,rep_file in enumerate(rep_strategy):
        rep_data_raw[i].append(pd.read_csv(rep_file))
        
    
for i,rep_strategy in enumerate(rep_data_raw):
    for j,rep_data in enumerate(rep_strategy):
        rep_data_observe[i].append(rep_data[(rep_data.Calendar >= rep_data_range[0]) & (rep_data.Calendar <= rep_data_range[1])])
        rep_headers = rep_data.columns
     

for i,rep_strategy in enumerate(rep_data_observe):
    for j,rep_data in enumerate(rep_strategy):
        rep_data_concat[i].append(rep_data)         
    rep_data_mean_observe[i].append(pd.concat(rep_data_concat[i]).mean(level=0))
    rep_data_min_observe[i].append(pd.concat(rep_data_concat[i]).min(level=0)) 
    rep_data_max_observe[i].append(pd.concat(rep_data_concat[i]).max(level=0))
   
rep_data_concat = []
rep_data_raw = []
rep_data_observe = []

for i,rep_strategy in enumerate(rep_data_mean_observe):
    for j,rep_data in enumerate(rep_strategy):
        rep_data["Year"] = rep_data.Calendar - rep_data_range[0]
for i,rep_strategy in enumerate(rep_data_max_observe):
    for j,rep_data in enumerate(rep_strategy):
        rep_data["Year"] = rep_data.Calendar - rep_data_range[0]
for i,rep_strategy in enumerate(rep_data_min_observe):
    for j,rep_data in enumerate(rep_strategy):
        rep_data["Year"] = rep_data.Calendar - rep_data_range[0]
        

#Plot vars
plot_lines = []
plot_labels = []
ops = { 
       "+": operator.add, 
       "-": operator.sub,
       "x": operator.mul,
       "/": operator.truediv
       }

def plot_one_header_CI(header, data, tag_index, header_index, confident_interval):
    if "ByLocation" in header:
        for location_index in rep_locations[tag_index]: 
            sns.lineplot(data = data[0], 
                        x = rep_x_observe,
                        y = header+str(location_index),
                        ax = axes[header_index,tag_index],
                        ci = confident_interval) 
    else:
        sns.lineplot(data = data[0], 
                    x = rep_x_observe,
                    y = header,
                    ax = axes[header_index,tag_index],
                    ci = confident_interval)
    
def plot_two_headers_ops(header1, header2, data, tag_index, op, header_index, confident_interval):
    if "ByLocation" in header1:
        for location_index in rep_locations[tag_index]:                    
              sns.lineplot(data = data[0], 
                        x = rep_x_observe,
                        y = ops[op](data[0][header1+str(location_index)],
                                    data[0][header2+str(location_index)]),
                        ax = axes[header_index,tag_index],
                        ci = confident_interval)
    else:
        sns.lineplot(data = data[0], 
                    x = rep_x_observe,
                    y = ops[op](data[0][header1],
                                data[0][header2]),
                    ax = axes[header_index,tag_index],
                    ci = confident_interval)
    if header_index == 0:        
        axes[header_index,tag_index].set_title(rep_strategies[tag_index] + "_" + rep_tag)
    axes[header_index,tag_index].set_ylabel(short_header(header1)+ op +short_header(header2))
        
def plot_one_header(header, data, tag_index, header_index, confident_interval):
    plot_one_header_CI(header, data, tag_index, header_index,confident_interval)
    if header_index == 0:        
        axes[header_index,tag_index].set_title(rep_strategies[tag_index] + "_" + rep_tag)
    axes[header_index,tag_index].set_ylabel(short_header(header))
    
def plot_headers(header, data, tag_index, header_index, confident_interval):
    if type(header) is list:
        plot_two_headers_ops(header[0], header[1], data, tag_index, header[2], header_index, confident_interval)
    else:
        plot_one_header(header, data, tag_index, header_index, confident_interval)
            
        
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
                        "BloodSlidePrevalenceByLocation",
                        "ProbabilityToBeTreatedLT5ByLocation",
                        "CumulativeMutantsByLocation",
                        "TotalParasitePopulationByLocation",
                        "MonthlyNumberOfTreatmentByLocation",
                        "MonthlyNumberOfTreatmentFailureByLocation", 
                        "MalariaDeathsByLocation",
                        ]

fig, axes = plt.subplots(nrows=len(rep_header_observe), 
                         ncols=len(rep_strategies),
                         sharex=True, sharey="row", 
                         figsize = (300,100))
fig.subplots_adjust(top = 0.94, bottom = 0.06, right = 0.95, left = 0.05, hspace=0.1, wspace = 0.1)
# sns.set_style("darkgrid")
   
#Ploting
for tag_index in range(len(rep_strategies)):
    for header_index,header in enumerate(rep_header_observe):
        plot_headers(header, rep_data_mean_observe[tag_index], tag_index, header_index, confident_interval)
        
plt.xticks(x_tick_observe)
fig.legend(loc='lower center', labels=[str(i+1) for i in rep_locations[0]], ncol = len(rep_strategies))
    