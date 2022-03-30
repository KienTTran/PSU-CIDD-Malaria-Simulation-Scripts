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
rep_month = "12"
rep_day = "07"
rep_hour = "21"
rep_minute = "52"
rep_total_location = 1
rep_therapy_id = 1
rep_prmc_size = 500
rep_if_rate = 0.19
rep_data_range = [2007,2107]
rep_jobs = 1
rep_date = rep_year + "_" + rep_month + "_" + rep_day + "_" + rep_hour + "_" + rep_minute 
rep_tags = [
            "PRMC_WI_NT_NS",
            ]
rep_base_name = "Daily_PRMC_Data"
rep_ext = ".txt"
rep_prefix = "../output/"
rep_files = []

# rep_x_observe = "Calendar"
rep_x_observe = "Year"
# rep_x_observe = "Day"


#Data vars
rep_data_raw = []
rep_data_observe = []
rep_data_mean_observe = []
rep_locations = [
                  [0]
                ]
rep_headers = []

#Plot
rep_location_colors = [ "cyan", "orange", "green", "purple", "yellow", "red" ]
                        
for job in range(0,rep_jobs):
    for tag in rep_tags:
        rep_files.append(rep_prefix + rep_date + "_" + rep_base_name + "_" 
                # + str(rep_total_location) + "_" 
                # + str(rep_therapy_id) + "_" 
                # + str(rep_prmc_size) + "_" 
                # + str(rep_if_rate) + "_" 
                + tag + "_"
                + str(job) + rep_ext)
                
for rep_file in rep_files:
    rep_data_raw.append(pd.read_csv(rep_file))
    
for data in rep_data_raw:
    rep_data_observe.append(data[(data.Calendar >= rep_data_range[0]) & (data.Calendar <= rep_data_range[1])])

rep_headers = rep_data_raw[0].columns
                  
# rep_data_mean_observe = rep_data_observe[0]

#Change data to frequency
for data in rep_data_observe:
    data.iloc[:, 3:] = data.iloc[:, 3:] / rep_prmc_size

rep_data_concat = [rep_data for rep_data in rep_data_observe]             
rep_data_mean_observe = pd.concat(rep_data_concat).mean(level=0)            
# rep_data_min_observe = pd.concat(rep_data_concat).min(level=0)          
# rep_data_max_observe = pd.concat(rep_data_concat).max(level=0)         
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
        
def plot_one_header_CI(data, col_index, row_index, location_index, confident_interval):
    axis = axes[row_index,col_index] if rep_cols_observe > 1 else axes
    for header in rep_header_observe:
        if header[0] == str(location_index):
            # print(str(location_index) + ": " + header)
            # data.T.plot(kind='bar',stacked=True)
            # print(header[2:])
            # axis.bar(data.index, data[header], label=header)
            sns.lineplot(data = data, 
                        x = rep_x_observe,
                        y = header,
                        ax = axis,
                        ci = confident_interval,
                        # err_style='bars'
                        ) 
        
def plot_one_header(title, data, col_index, row_index, location_index, confident_interval):
    plot_one_header_CI(data, col_index, row_index, location_index, confident_interval)
    axis = axes[row_index,col_index] if rep_cols_observe > 1 else axes
    axis.set_title(title,fontsize=8)
    axis.set_ylabel(None)
    
def plot_headers(title, data, col_index, row_index, location_index, confident_interval):
    plot_one_header(title, data, col_index, row_index, location_index, confident_interval)
        
# x_tick_observe = range(rep_data_range[0],rep_data_range[1],5)
x_tick_observe = []

if rep_x_observe == "Year":
    x_tick_observe = range(0,rep_data_range[1]-rep_data_range[0],5)   
    # for year in rep_data_mean_observe[0][0].Calendar:
    #     x_tick_observe.append(year - rep_data_range[0])
else:
    x_tick_observe = range(rep_data_range[0],rep_data_range[1],5)   

#None/sd
confident_interval = None

rep_header_observe = rep_headers[2:len(rep_headers)]

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
        
plt.xticks(x_tick_observe)
fig.legend(loc='lower center', labels=[str(i) for i in rep_header_legend], ncol = len(rep_tags))