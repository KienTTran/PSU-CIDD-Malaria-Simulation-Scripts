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

#Data vars
def plot_rep_from_file(rep_file, delay):
    rep_tag = ""  
    rep_tags = []
    print(rep_file)
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
    rep_data_range = [2007,2537]
    rep_total_location = 1  
    rep_data_csv = 0
    
    #Plot
    rep_location_colors = [ "cyan", "orange", "green", "purple", "yellow", "red" ]
                   
    try:
        rep_data_csv = pd.read_csv(rep_file)
    except pd.errors.EmptyDataError:
        print('Empty csv file!')
        return
         
    rep_data_raw.append(rep_data_csv)
        
    for data in rep_data_raw:
        rep_data_observe.append(data)
    
    rep_headers = rep_data_raw[0].columns
    
    #Change data to frequency
    for data in rep_data_observe:
        sum = data.iloc[:, 4:].sum(axis=1)
        data.iloc[:, 4:] = data.iloc[:, 4:].div(sum, axis='index')
                      
    # rep_data_mean_observe = rep_data_observe[0]
    
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
            
    # rep_x_observe = "Calendar"
    rep_x_observe = "Year"
    # rep_x_observe = "Day"
    
    # x_tick_observe = range(rep_data_range[0],rep_data_range[1],5)
    x_tick_observe = []
    y_tick_observe = [x * 0.1 for x in range(0, 10)]
    
    if rep_x_observe == "Year":
        x_tick_observe = range(0,rep_data_range[1] - rep_data_range[0],10)  
    else:
        x_tick_observe = range(rep_data_range[0],rep_data_range[1],30) 
        
    
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
            plot_headers(rep_tag, rep_data_mean_observe, col_index, row_index, location_index, confident_interval)
            
    plt.xticks(x_tick_observe)
    plt.yticks(y_tick_observe)
    fig.legend(loc='right', labels=[str(i) for i in rep_header_legend], ncol = 1)
    plt.pause(delay)