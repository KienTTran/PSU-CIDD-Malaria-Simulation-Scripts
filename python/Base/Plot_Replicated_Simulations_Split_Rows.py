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
import numpy as np

#Plot vars
plot_lines = []
plot_labels = []
ops = { 
        "+": operator.add, 
        "-": operator.sub,
        "x": operator.mul,
        "/": operator.truediv
        }
            
def plot_headers(title, data_mean, data_min, data_max, \
                    rep_cols_observe, col_index, row_index, \
                    rep_header_observe, rep_x_observe, axes, \
                    index, confident_interval):
    if index == 0:
        for header in rep_header_observe:
            sns.lineplot(data = data_mean, 
                        x = rep_x_observe,
                        y = header,
                        ax = axes[index],
                        ci = confident_interval,
                        linewidth = 1.0,
                        # linestyle="dashed"
                        # err_style='bars'
                        )
        axes[index].set_title("Allele Frequency",fontsize=12)
        axes[index].axhline(y=0.5, color='grey', linestyle='--', linewidth = 2.0, alpha = 0.4)
        axes[index].legend(loc='lower center', labels=[headers[2:] for headers in rep_header_observe], ncol = 2)
    elif index == 1:
        for header in rep_header_observe:
            sns.lineplot(data = data_mean, 
                        x = rep_x_observe,
                        y = header,
                        ax = axes[index],
                        ci = confident_interval,
                        linewidth = 1.0,
                        # err_style='bars'
                        )
        axes[index].set_title("Genotype Frequency",fontsize=12)
        axes[index].axhline(y=0.25, color='grey', linestyle='--', linewidth = 2.0, alpha = 0.4)
        axes[index].legend(loc='lower center', labels=[headers[2:] for headers in rep_header_observe], ncol = 2)
    else:
        for header in rep_header_observe:
            sns.lineplot(data = data_mean, 
                        x = rep_x_observe,
                        y = header,
                        ax = axes[index],
                        ci = confident_interval,
                        linewidth = 1.0,
                        # err_style='bars'
                        )
        axes[index].set_title("Linkage Disequilibrium",fontsize=12)
        axes[index].tick_params(which="both", bottom=True)
        axes[index].legend(loc='center', labels=[headers[2:] for headers in rep_header_observe], ncol = 2)
        axes[index].set_xlabel(None)
    axes[index].set_ylabel(None) 
        
    
#Data vars
def plot_replicated_simulations(rep_files, delay, start_year, end_year, display, year_interval, month_interval, day_interval):
    rep_tag = ""  
    rep_tags = []
    print(rep_files)
    for rep_file in rep_files:        
        for split_items_1 in rep_file.split("/"):
            if "\\" in split_items_1:
                rep_tags = split_items_1.split("\\")
                rep_tag = rep_tags[-3]
            else:
                rep_tags = rep_file.split("/")
                rep_tag = rep_tags[-1]
    
    rep_tag_data = rep_tag.split("_")
    print(rep_tag_data)

    rep_data_raw = []
    rep_data_observe = []
    rep_data_mean_observe = []
    rep_locations = [
                      [0,1,2,3]
                    ]
    rep_headers = []  
    rep_header_legend = []
    rep_data_range = [start_year, end_year]
    rep_total_location = 1  
    rep_data_csv = 0
    
    #Plot
    rep_location_colors = [ "cyan", "orange", "green", "purple", "yellow", "red" ]
                   
    try:
        for rep_file in rep_files:
            rep_data_csv = pd.read_csv(rep_file)             
            rep_data_raw.append(rep_data_csv)
    except pd.errors.EmptyDataError:
        print('Empty csv file!')
        return
        
    for data in rep_data_raw:
        rep_data_observe.append(data[(data.Calendar >= rep_data_range[0]) & (data.Calendar <= rep_data_range[1])])
    
    #Change data to frequency
    for data in rep_data_observe:
        sum = data.iloc[:, 2:].sum(axis=1)
        
        data["First"] = data['Day'].apply(lambda x: data.Day[0:1])
        data["Year"] = data.Calendar - rep_data_range[0]
        data["Month"] = (data.Day - data.First) / 30
        data["Month"] = data["Month"].round(0)
        data["Day"] = data.Day - data.First
        del data['First']
        
        #Calculate allele frequency
        data["0:Allele K"] = (data["0:KYY--C1x"] + data["0:KYY--Y1x"])/sum
        data["0:Allele C"] = (data["0:KYY--C1x"] + data["0:TYY--C1x"])/sum
        data["0:Allele T"] = (data["0:TYY--C1x"] + data["0:TYY--Y1x"])/sum
        data["0:Allele Y"] = (data["0:KYY--Y1x"] + data["0:TYY--Y1x"])/sum
        
        data["0:KYY--C1x "] = data["0:KYY--C1x"]
        data["0:KYY--Y1x "] = data["0:KYY--Y1x"]
        data["0:TYY--C1x "] = data["0:KYY--C1x"]
        data["0:TYY--Y1x "] = data["0:KYY--Y1x"]
                
        #Calculate genotype frequency
        data.iloc[:, 12:] = data.iloc[:, 2:].div(sum, axis='index')
        
        #Calculate LD
        data["0:[KC] - [K][C]"] = data["0:KYY--C1x "] - (data["0:Allele K"]*data["0:Allele C"])
        data["0:[TY] - [T][Y]"] = data["0:TYY--Y1x "] - (data["0:Allele T"]*data["0:Allele Y"])
        
    rep_headers = rep_data_observe[0].columns
    print(rep_headers)
    
    rep_data_concat = [rep_data for rep_data in rep_data_observe]             
    rep_data_mean_observe = pd.concat(rep_data_concat).median(level=0)            
    rep_data_min_observe = pd.concat(rep_data_concat).min(level=0)          
    rep_data_max_observe = pd.concat(rep_data_concat).max(level=0)         
    rep_data_quantile_observe = pd.concat(rep_data_concat).quantile(axis=0)
    
    #Test
    # rep_data_mean_observe = rep_data_observe[0]        
    
    # x_tick_observe = range(rep_data_range[0],rep_data_range[1],5)
    x_tick_observe = []
    y_tick_observe = [x * 0.1 for x in range(0, 6)]
    
    if display == "Year":
        x_tick_observe = range(0,int(rep_data_mean_observe["Year"].tail(1)) + 1, year_interval)  
    elif display == "Month":
        x_tick_observe = range(0,int(rep_data_mean_observe["Month"].tail(1)) + 1, month_interval) 
    else:
        x_tick_observe = range(0,int(rep_data_mean_observe["Day"].tail(1)) + 1, day_interval) 
        
    
    #None/sd
    confident_interval = None
    rep_header_observe = []
    rep_header_observe.append(rep_headers[10:14]) #index 0
    rep_header_observe.append(rep_headers[14:18]) #index 1
    
    rep_header_legend = []
    
    for index in range(0,int((len(rep_header_observe))/rep_total_location)):
        rep_header_legend.append(rep_header_observe[index][2:])
    
    rep_rows_observe = 3
    rep_cols_observe = 1
    
    fig, axes = plt.subplots(nrows=rep_rows_observe, 
                              ncols=rep_cols_observe,
                              sharex="col", sharey=False, 
                              figsize = (300,100),
                              gridspec_kw={'height_ratios': [1,3]})
    fig.subplots_adjust(top = 0.94, bottom = 0.06, right = 0.95, left = 0.05, 
                        hspace=0.05, wspace = 0.2)
    sns.set_style("darkgrid")
       
    #Ploting
    for col_index in range(0,rep_cols_observe):
        for row_index in range(0,rep_rows_observe):
            index = col_index + row_index * rep_cols_observe
            plot_headers(rep_tag, rep_data_mean_observe, rep_data_min_observe, rep_data_max_observe, \
                         rep_cols_observe, col_index, row_index, \
                         rep_header_observe[index], display, axes, \
                         index, confident_interval)
            
    plt.xticks(x_tick_observe)
    # plt.yticks(y_tick_observe)    
    plt.pause(delay)