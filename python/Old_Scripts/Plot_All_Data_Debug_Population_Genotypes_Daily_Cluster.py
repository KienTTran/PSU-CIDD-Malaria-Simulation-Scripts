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
import matplotlib.dates as mdates
import matplotlib.ticker as ticker

#File vars
rep_year = "2022"
rep_month = "02"
rep_day = "04"
rep_hour = "14"
rep_minute = "44"
rep_total_location = 1
rep_population = 1000000
rep_beta = 0.3
rep_therapy_id = 0
rep_prmc_size = 800
rep_prmc_start_year= "2007"
rep_prmc_end_year= "2027"
rep_if_rate = 0.99
rep_data_range = [2007,2027]
rep_jobs = 1
rep_date = rep_year + "_" + rep_month + "_" + rep_day + "_" + rep_hour + "_" + rep_minute 
rep_tags = [
            # "PRMC_Nguyen_Interrupted"
            # "PRMC_Nguyen_No_Interrupted_0.2"
            # "PRMC"
            "PRMC_Kien_Parasite_Id_1M"
            # "PRMC_Kien_PRMC_Id_iG2"
            # "PRMC_Kien_PRMC_Id"
            + "_" + str(rep_prmc_size) 
            + "_" + str(rep_if_rate) 
            + "_" + str(rep_beta)
            + "_" + rep_prmc_start_year
            + "_" + rep_prmc_end_year,
            ]
rep_base_name = "Daily_PG_Data"
# rep_base_name = "Daily_Population_Genotypes_Data"
rep_ext = ".txt"
rep_prefix = "D:/plot/new/1M/Parasite/"
# rep_prefix = "D:/plot/new/1M/PRMC/"
rep_files = []

#Data vars
rep_data_raw = []
rep_data_observe = []
rep_data_mean_observe = []
rep_locations = [
                  [0,1,2,3]
                ]
rep_headers = []

#Plot
rep_location_colors = [ "cyan", "orange", "green", "purple", "yellow", "red" ]
                        
for job in range(rep_jobs,rep_jobs+1):
    for tag in rep_tags:
        rep_files.append(rep_prefix + tag + "/output/" + rep_date + "_" + rep_base_name + "_" 
                + str(rep_total_location) + "_" 
                + str(rep_population) + "_" 
                + str(rep_beta) + "_" 
                + str(rep_therapy_id) + "_" 
                + str(rep_prmc_size) + "_" 
                + str(rep_if_rate) + "_" 
                + str(rep_prmc_start_year) + "_" 
                + str(rep_prmc_end_year) + "_" 
                + tag + "_"
                + str(job) + rep_ext)
                
for rep_file in rep_files:
    rep_data_raw.append(pd.read_csv(rep_file))
    
for data in rep_data_raw:
    rep_data_observe.append(data[(data.Calendar >= rep_data_range[0]) & (data.Calendar <= rep_data_range[1])])


#Change data to frequency
for data in rep_data_observe:
    sum = data.iloc[:, 4:].sum(axis=1)
    
    data["First"] = data['Day'].apply(lambda x: data.Day[0:1])
    data["Year"] = data.Calendar - rep_data_range[0]
    data["Month"] = (data.Day - data.First) / 30
    data["Month"] = data["Month"].round(0)
    data["Day"] = data.Day - data.First
    del data['First']
   
    data["0:Allele_K"] = (data["0:KYY--C1x"] + data["0:KYY--Y1x"])/sum
    data["0:Allele_C"] = (data["0:KYY--C1x"] + data["0:TYY--C1x"])/sum
    data["0:Allele_T"] = (data["0:TYY--C1x"] + data["0:TYY--Y1x"])/sum
    data["0:Allele_Y"] = (data["0:KYY--Y1x"] + data["0:TYY--Y1x"])/sum
    
    data["0:KYY--C1x2"] = data["0:KYY--C1x"]
    data["0:KYY--Y1x2"] = data["0:KYY--Y1x"]
    data["0:TYY--C1x2"] = data["0:KYY--C1x"]
    data["0:TYY--Y1x2"] = data["0:KYY--Y1x"]
    
    data.iloc[:, 14:] = data.iloc[:, 4:].div(sum, axis='index')
    
    data["0:KC-[K][C]"] = data["0:KYY--C1x2"] - (data["0:Allele_K"]*data["0:Allele_C"])
    data["0:TY-[T][Y]"] = data["0:TYY--Y1x2"] - (data["0:Allele_T"]*data["0:Allele_Y"])
    
    # print(sum_k)


rep_headers = rep_data_observe[0].columns
             
# rep_data_mean_observe = rep_data_observe[0]

rep_data_concat = [rep_data for rep_data in rep_data_observe]             
rep_data_mean_observe = pd.concat(rep_data_concat).mean(level=0)            
# rep_data_min_observe = pd.concat(rep_data_concat).min(level=0)          
# rep_data_max_observe = pd.concat(rep_data_concat).max(level=0)         
# rep_data_quantile_observe = pd.concat(rep_data_concat).quantile(axis=0)
    
# rep_data_mean_observe["Year"] = rep_data_mean_observe.Calendar - rep_data_range[0]
# rep_data_mean_observe["Month"] = rep_data_mean_observe.Day / 30
# rep_data_mean_observe["Month"] = rep_data_mean_observe["Month"].round(0)
        
#Plot vars
plot_lines = []
plot_labels = []
ops = { 
       "+": operator.add, 
       "-": operator.sub,
       "x": operator.mul,
       "/": operator.truediv
       }

major_ticks = []
major_tick_labels = []
minor_ticks = []
minor_tick_labels = []

for month in range(0,int(rep_data_mean_observe.Month.tail(1))):
    print(month)
    major_ticks.append(month)
    if month % 12 == 0:
        major_ticks.append(int(month/12))
    
        
def plot_one_header_CI(data, col_index, row_index, location_index, confident_interval):
    axis = axes[row_index,col_index] if rep_cols_observe > 1 else axes
    for header in rep_header_observe:
        if header[0] == str(location_index):
            # print(str(location_index) + ": " + header)
            sns.lineplot(data = data, 
                        x = data.Month,
                        y = header,
                        ax = axis,
                        ci = confident_interval,
                        # err_style='bars'
                        )       
    axis.tick_params(which="both", bottom=True)
    # axis.set_xticks(major_ticks)
    # axis.set_xticklabels(major_tick_labels)
    # axis.set_xticks(minor_ticks, minor=True)
    # axis.set_xticklabels(minor_tick_labels, minor=True)
        
def plot_one_header(title, data, col_index, row_index, location_index, confident_interval):
    plot_one_header_CI(data, col_index, row_index, location_index, confident_interval)
    axis = axes[row_index,col_index] if rep_cols_observe > 1 else axes
    axis.set_title(title,fontsize=8)
    axis.set_ylabel(None)
    
def plot_headers(title, data, col_index, row_index, location_index, confident_interval):
    plot_one_header(title, data, col_index, row_index, location_index, confident_interval)
        
x_tick_major = []
x_tick_major_label = []
y_tick_major = [x * 0.1 for x in range(0, 7)]
    
for month in range(0,int(rep_data_mean_observe.Month.tail(1))):
    if month % 24 == 0:
        x_tick_major.append(month)
        x_tick_major_label.append(2007 + int(month/12))

#None/sd
confident_interval = None

rep_header_observe = rep_headers[10:20]

rep_header_legend = []

for index in range(0,int((len(rep_header_observe))/rep_total_location)):
    rep_header_legend.append(rep_header_observe[index][2:])

rep_rows_observe = 1
rep_cols_observe = 1

fig, axes = plt.subplots(nrows=rep_rows_observe, 
                         ncols=rep_cols_observe,
                         sharex="col", sharey=False, 
                         figsize = (300,100))
fig.subplots_adjust(top = 0.94, bottom = 0.06, right = 0.95, left = 0.05, hspace=0.2, wspace = 0.2)
sns.set_style("darkgrid")
   
#Ploting
for col_index in range(0,rep_cols_observe):
    for row_index in range(0,rep_rows_observe):
        location_index = col_index + row_index * rep_cols_observe
        plot_headers(rep_tags[0] + " location " + str(location_index) + ", PRMC size: " + str(rep_prmc_size), rep_data_mean_observe, col_index, row_index, location_index, confident_interval)
        
plt.minorticks_on()
plt.xticks(x_tick_major,x_tick_major_label)
plt.yticks(y_tick_major)
fig.legend(loc='right', labels=[str(i) for i in rep_header_legend], ncol = len(rep_tags))